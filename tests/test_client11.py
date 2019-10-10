
import pytest
import responses

from libtaxii import messages_11 as tm11

from cabby import create_client
from cabby import exceptions as exc
from cabby import entities
from cabby.constants import (
    XML_11_BINDING, SVC_INBOX, SVC_DISCOVERY, RT_COUNT_ONLY
)

from fixtures11 import (
    HOST, CONTENT_BINDING, POLL_RESPONSE, POLL_RESPONSE_WITH_MORE_1,
    POLL_RESPONSE_WITH_MORE_2, INBOX_RESPONSE, SUBSCRIPTION_ID,
    COLLECTION_MANAGEMENT_RESPONSE,
    POLL_PATH, COLLECTION_MANAGEMENT_PATH, DISCOVERY_RESPONSE,
    SUBSCRIPTION_RESPONSE, DISCOVERY_PATH, CONTENT_BLOCKS,
    CONTENT, COLLECTION_MANAGEMENT_URI, DISCOVERY_URI_HTTP,
    DISCOVERY_URI_HTTPS, INBOX_URI, POLL_URI, POLL_COLLECTION)


# Utils


def create_client_11(**kwargs):
    client = create_client(HOST, version="1.1", **kwargs)
    return client


def register_uri(uri, body, **kwargs):
    responses.add(
        method=responses.POST,
        url=uri,
        body=body,
        content_type='application/xml',
        stream=True,
        adding_headers={'X-TAXII-Content-Type': XML_11_BINDING},
        **kwargs)


def get_sent_message():
    body = responses.calls[-1].request.body
    print(repr(body))
    return tm11.get_message_from_xml(body)


# Tests


def test_no_discovery_path():
    client = create_client_11()

    with pytest.raises(exc.NoURIProvidedError):
        client.discover_services()


def test_no_discovery_path_when_pushing():
    client = create_client_11()

    with pytest.raises(exc.NoURIProvidedError):
        client.push(CONTENT, CONTENT_BINDING)


@responses.activate
def test_incorrect_path():

    responses.add(responses.POST, DISCOVERY_URI_HTTP, status=404)

    client = create_client_11(discovery_path=DISCOVERY_PATH)

    with pytest.raises(exc.HTTPError):
        client.discover_services()


@responses.activate
def test_discovery():

    register_uri(DISCOVERY_URI_HTTP, DISCOVERY_RESPONSE)

    client = create_client_11(discovery_path=DISCOVERY_PATH)

    services = client.discover_services()

    assert len(services) == 4
    assert all([
        isinstance(s, entities.DetailedServiceInstance) for s in services
    ])

    assert len([s for s in services if s.type == SVC_INBOX]) == 1
    assert len([s for s in services if s.type == SVC_DISCOVERY]) == 2

    message = get_sent_message()

    assert type(message) == tm11.DiscoveryRequest


@responses.activate
def test_discovery_https():

    register_uri(DISCOVERY_URI_HTTPS, DISCOVERY_RESPONSE)

    client = create_client_11(discovery_path=DISCOVERY_PATH, use_https=True)

    services = client.discover_services()

    assert len(services) == 4

    message = get_sent_message()
    assert type(message) == tm11.DiscoveryRequest


@responses.activate
def test_collections():

    register_uri(COLLECTION_MANAGEMENT_URI, COLLECTION_MANAGEMENT_RESPONSE)

    client = create_client_11()

    collections = client.get_collections(uri=COLLECTION_MANAGEMENT_PATH)

    assert len(collections) == 2
    assert all([c.type == entities.Collection.TYPE_FEED for c in collections])

    message = get_sent_message()
    assert type(message) == tm11.CollectionInformationRequest


@responses.activate
def test_collections_with_automatic_discovery():

    register_uri(DISCOVERY_URI_HTTP, DISCOVERY_RESPONSE)
    register_uri(COLLECTION_MANAGEMENT_URI, COLLECTION_MANAGEMENT_RESPONSE)

    client = create_client_11(discovery_path=DISCOVERY_URI_HTTP)

    response = client.get_collections()

    assert len(response) == 2

    message = get_sent_message()
    assert type(message) == tm11.CollectionInformationRequest


@responses.activate
def test_poll():

    register_uri(POLL_URI, POLL_RESPONSE)

    client = create_client_11()
    blocks = list(client.poll(POLL_COLLECTION, uri=POLL_PATH))

    assert len(blocks) == 2

    message = get_sent_message()
    assert type(message) == tm11.PollRequest
    assert message.collection_name == POLL_COLLECTION


@responses.activate
def test_poll_count_only():

    register_uri(POLL_URI, POLL_RESPONSE)

    client = create_client_11()
    count = client.get_content_count(POLL_COLLECTION, uri=POLL_PATH)

    assert count.count == 2
    assert not count.is_partial

    message = get_sent_message()
    assert type(message) == tm11.PollRequest
    assert message.collection_name == POLL_COLLECTION
    assert message.poll_parameters.response_type == RT_COUNT_ONLY


@responses.activate
def test_poll_with_subscription():

    register_uri(POLL_URI, POLL_RESPONSE)

    client = create_client_11()
    blocks = list(client.poll(POLL_COLLECTION,
                              subscription_id=SUBSCRIPTION_ID,
                              uri=POLL_PATH))

    assert len(blocks) == 2

    message = get_sent_message()
    assert type(message) == tm11.PollRequest
    assert message.collection_name == POLL_COLLECTION
    assert message.subscription_id == SUBSCRIPTION_ID


@responses.activate
def test_poll_with_delivery():

    register_uri(DISCOVERY_URI_HTTP, DISCOVERY_RESPONSE)
    register_uri(POLL_URI, POLL_RESPONSE)

    client = create_client_11(discovery_path=DISCOVERY_PATH)

    services = client.discover_services()

    inbox = next((s for s in services if s.type == SVC_INBOX), None)

    blocks = list(client.poll(POLL_COLLECTION,
                              inbox_service=inbox,
                              uri=POLL_PATH))

    assert len(blocks) == 2

    message = get_sent_message()
    assert type(message) == tm11.PollRequest
    assert message.collection_name == POLL_COLLECTION
    returned_addr = message.poll_parameters.delivery_parameters.inbox_address
    assert returned_addr == inbox.address
    assert message.poll_parameters.allow_asynch is True


@responses.activate
def test_poll_with_fullfilment():

    register_uri(POLL_URI, POLL_RESPONSE_WITH_MORE_1)

    client = create_client_11()

    gen = client.poll(POLL_COLLECTION, uri=POLL_PATH)
    block_1 = next(gen)

    assert block_1.content.decode('utf-8') == CONTENT_BLOCKS[0]

    message = get_sent_message()
    assert type(message) == tm11.PollRequest
    assert message.collection_name == POLL_COLLECTION

    responses.remove(responses.POST, POLL_URI)
    register_uri(POLL_URI, POLL_RESPONSE_WITH_MORE_2)
    block_2 = next(gen)

    assert block_2.content.decode('utf-8') == CONTENT_BLOCKS[1]

    message = get_sent_message()
    assert type(message) == tm11.PollFulfillmentRequest
    assert message.collection_name == POLL_COLLECTION
    assert message.result_part_number == 2


@responses.activate
def test_poll_with_content_bindings():

    register_uri(POLL_URI, POLL_RESPONSE_WITH_MORE_1)

    client = create_client_11()

    gen = client.poll(POLL_COLLECTION, uri=POLL_PATH,
                      content_bindings=[CONTENT_BINDING])

    block_1 = next(gen)
    assert block_1.content.decode('utf-8') == CONTENT_BLOCKS[0]

    message = get_sent_message()
    assert type(message) == tm11.PollRequest
    assert message.collection_name == POLL_COLLECTION

    poll_params = message.poll_parameters
    assert len(poll_params.content_bindings) == 1
    assert poll_params.content_bindings[0].binding_id == CONTENT_BINDING

    subtypes = ['some-subtype-a', 'some-subtype-b']
    binding = entities.ContentBinding(CONTENT_BINDING, subtypes=subtypes)

    gen = client.poll(POLL_COLLECTION, uri=POLL_PATH,
                      content_bindings=[binding])

    block_1 = next(gen)
    assert block_1.content.decode('utf-8') == CONTENT_BLOCKS[0]

    message = get_sent_message()
    assert type(message) == tm11.PollRequest

    poll_params = message.poll_parameters
    assert len(poll_params.content_bindings) == 1
    assert poll_params.content_bindings[0].binding_id == binding.id
    assert poll_params.content_bindings[0].subtype_ids == binding.subtypes


@responses.activate
def test_subscribe():

    register_uri(COLLECTION_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)

    client = create_client_11()
    response = client.subscribe(POLL_COLLECTION,
                                uri=COLLECTION_MANAGEMENT_PATH)

    assert response.collection_name == POLL_COLLECTION

    message = get_sent_message()
    assert type(message) == tm11.ManageCollectionSubscriptionRequest
    assert message.collection_name == POLL_COLLECTION
    assert message.action == tm11.ACT_SUBSCRIBE


@responses.activate
def test_subscribe_with_push():

    register_uri(COLLECTION_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)
    register_uri(DISCOVERY_URI_HTTP, DISCOVERY_RESPONSE)

    client = create_client_11(discovery_path=DISCOVERY_PATH)

    services = client.discover_services()

    inbox = next((s for s in services if s.type == SVC_INBOX), None)

    response = client.subscribe(POLL_COLLECTION,
                                inbox_service=inbox,
                                uri=COLLECTION_MANAGEMENT_PATH)

    assert response.collection_name == POLL_COLLECTION

    message = get_sent_message()
    assert type(message) == tm11.ManageCollectionSubscriptionRequest
    assert message.collection_name == POLL_COLLECTION
    assert message.push_parameters.inbox_address == inbox.address
    assert message.action == tm11.ACT_SUBSCRIBE


@responses.activate
def test_subscribtion_status():

    register_uri(COLLECTION_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)

    client = create_client_11()

    response = client.get_subscription_status(POLL_COLLECTION,
                                              subscription_id=SUBSCRIPTION_ID,
                                              uri=COLLECTION_MANAGEMENT_PATH)

    assert response.collection_name == POLL_COLLECTION

    message = get_sent_message()
    assert type(message) == tm11.ManageCollectionSubscriptionRequest
    assert message.collection_name == POLL_COLLECTION
    assert message.action == tm11.ACT_STATUS


@responses.activate
def test_unsubscribe():

    register_uri(COLLECTION_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)

    client = create_client_11()

    response = client.unsubscribe(POLL_COLLECTION,
                                  subscription_id=SUBSCRIPTION_ID,
                                  uri=COLLECTION_MANAGEMENT_PATH)

    assert response.collection_name == POLL_COLLECTION
    assert len(response.subscriptions) == 1
    subscription = response.subscriptions[0]
    assert subscription.subscription_parameters.response_type == \
        entities.SubscriptionParameters.TYPE_FULL

    message = get_sent_message()
    assert type(message) == tm11.ManageCollectionSubscriptionRequest
    assert message.collection_name == POLL_COLLECTION
    assert message.action == tm11.ACT_UNSUBSCRIBE


@responses.activate
def test_pause_subscription():

    register_uri(COLLECTION_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)

    client = create_client_11()

    response = client.pause_subscription(POLL_COLLECTION,
                                         subscription_id=SUBSCRIPTION_ID,
                                         uri=COLLECTION_MANAGEMENT_PATH)

    assert response.collection_name == POLL_COLLECTION

    message = get_sent_message()
    assert type(message) == tm11.ManageCollectionSubscriptionRequest
    assert message.collection_name == POLL_COLLECTION
    assert message.action == tm11.ACT_PAUSE


@responses.activate
def test_resume_subscription():

    register_uri(COLLECTION_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)

    client = create_client_11()

    response = client.resume_subscription(POLL_COLLECTION,
                                          subscription_id=SUBSCRIPTION_ID,
                                          uri=COLLECTION_MANAGEMENT_PATH)

    assert response.collection_name == POLL_COLLECTION

    message = get_sent_message()
    assert type(message) == tm11.ManageCollectionSubscriptionRequest
    assert message.collection_name == POLL_COLLECTION
    assert message.action == tm11.ACT_RESUME


@responses.activate
def test_push():

    register_uri(INBOX_URI, INBOX_RESPONSE)

    client = create_client_11()

    client.push(CONTENT, CONTENT_BINDING, uri=INBOX_URI)

    message = get_sent_message()

    assert type(message) == tm11.InboxMessage
    assert len(message.content_blocks) == 1
    assert message.content_blocks[0].content == CONTENT
    binding = message.content_blocks[0].content_binding.binding_id
    assert binding == CONTENT_BINDING


@responses.activate
def test_push_with_destination():

    register_uri(INBOX_URI, INBOX_RESPONSE)

    client = create_client_11()
    dest_collections = [POLL_COLLECTION]

    client.push(CONTENT, CONTENT_BINDING,
                collection_names=dest_collections, uri=INBOX_URI)

    message = get_sent_message()

    assert type(message) == tm11.InboxMessage
    assert len(message.content_blocks) == 1
    assert message.content_blocks[0].content == CONTENT
    binding = message.content_blocks[0].content_binding.binding_id
    assert binding == CONTENT_BINDING

    assert message.destination_collection_names == dest_collections
