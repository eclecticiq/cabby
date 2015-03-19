import pytest
import httpretty

from itertools import ifilter

from libtaxii import messages_11 as tm11
from libtaxii.constants import *

from cabby import create_client
from cabby import exceptions as exc
from cabby import entities

from fixtures11 import *

### Utils

def create_client_11(**kwargs):
    client = create_client(HOST, version="1.1", **kwargs)
    return client


def register_uri(uri, body, **kwargs):
    httpretty.register_uri(httpretty.POST, uri, body=body, content_type='application/xml',
            adding_headers={'X-TAXII-Content-Type': VID_TAXII_XML_11}, **kwargs)


def get_sent_message():
    body = httpretty.last_request().body
    return tm11.get_message_from_xml(body)


### Tests

def test_no_discovery_path():
    client = create_client_11()

    with pytest.raises(exc.NoURIProvidedError):
        client.discover_services()


def test_no_discovery_path_when_pushing():
    client = create_client_11()

    with pytest.raises(exc.NoURIProvidedError):
        client.push(CONTENT, CONTENT_BINDING)


@httpretty.activate
def test_incorrect_path():

    httpretty.register_uri(httpretty.POST, DISCOVERY_URI_HTTP, status=404)

    client = create_client_11(discovery_path=DISCOVERY_PATH)

    with pytest.raises(exc.UnsuccessfulStatusError):
        client.discover_services()


@httpretty.activate
def test_discovery():

    register_uri(DISCOVERY_URI_HTTP, DISCOVERY_RESPONSE)

    client = create_client_11(discovery_path=DISCOVERY_PATH)

    services = client.discover_services()

    assert len(services) == 4
    assert all(map(lambda s: isinstance(s, entities.DetailedServiceInstance), services))

    assert len(filter(lambda s: s.type == SVC_INBOX, services)) == 1
    assert len(filter(lambda s: s.type == SVC_DISCOVERY, services)) == 2

    message = get_sent_message()

    assert type(message) == tm11.DiscoveryRequest


@httpretty.activate
def test_discovery_https():

    register_uri(DISCOVERY_URI_HTTPS, DISCOVERY_RESPONSE)

    client = create_client_11(discovery_path=DISCOVERY_PATH, use_https=True)

    services = client.discover_services()

    assert len(services) == 4

    message = get_sent_message()
    assert type(message) == tm11.DiscoveryRequest


@httpretty.activate
def test_collections():

    register_uri(COLLECTION_MANAGEMENT_URI, COLLECTION_MANAGEMENT_RESPONSE)

    client = create_client_11()

    collections = client.get_collections(uri=COLLECTION_MANAGEMENT_PATH)

    assert len(collections) == 2
    assert all(map(lambda c: c.type == entities.Collection.TYPE_FEED, collections))

    message = get_sent_message()
    assert type(message) == tm11.CollectionInformationRequest


@httpretty.activate
def test_collections_with_automatic_discovery():

    register_uri(DISCOVERY_URI_HTTP, DISCOVERY_RESPONSE)
    register_uri(COLLECTION_MANAGEMENT_URI, COLLECTION_MANAGEMENT_RESPONSE)

    client = create_client_11(discovery_path=DISCOVERY_URI_HTTP)

    response = client.get_collections()

    assert len(response) == 2

    message = get_sent_message()
    assert type(message) == tm11.CollectionInformationRequest


@httpretty.activate
def test_poll():

    register_uri(POLL_URI, POLL_RESPONSE)

    client = create_client_11()
    blocks = list(client.poll(POLL_COLLECTION, uri=POLL_PATH))

    assert len(blocks) == 2

    message = get_sent_message()
    assert type(message) == tm11.PollRequest
    assert message.collection_name == POLL_COLLECTION


@httpretty.activate
def test_poll_with_subscription():

    register_uri(POLL_URI, POLL_RESPONSE)

    client = create_client_11()
    blocks = list(client.poll(POLL_COLLECTION, subscription_id=SUBSCRIPTION_ID, uri=POLL_PATH))

    assert len(blocks) == 2

    message = get_sent_message()
    assert type(message) == tm11.PollRequest
    assert message.collection_name == POLL_COLLECTION
    assert message.subscription_id == SUBSCRIPTION_ID


@httpretty.activate
def test_poll_with_delivery():

    register_uri(DISCOVERY_URI_HTTP, DISCOVERY_RESPONSE)
    register_uri(POLL_URI, POLL_RESPONSE)

    client = create_client_11(discovery_path=DISCOVERY_PATH)

    services = client.discover_services()

    inbox = next(ifilter(lambda s: s.type == SVC_INBOX, services))

    blocks = list(client.poll(POLL_COLLECTION, inbox_service=inbox, uri=POLL_PATH))

    assert len(blocks) == 2

    message = get_sent_message()
    assert type(message) == tm11.PollRequest
    assert message.collection_name == POLL_COLLECTION
    assert message.poll_parameters.delivery_parameters.inbox_address == inbox.address
    assert message.poll_parameters.allow_asynch == True


@httpretty.activate
def test_poll_with_fullfilment():

    register_uri(POLL_URI, POLL_RESPONSE_WITH_MORE_1)

    client = create_client_11()

    gen = client.poll(POLL_COLLECTION, uri=POLL_PATH)
    block_1 = next(gen)

    assert block_1.content == CONTENT_BLOCKS[0]

    message = get_sent_message()
    assert type(message) == tm11.PollRequest
    assert message.collection_name == POLL_COLLECTION

    register_uri(POLL_URI, POLL_RESPONSE_WITH_MORE_2)
    block_2 = next(gen)
    
    assert block_2.content == CONTENT_BLOCKS[1]

    message = get_sent_message()
    assert type(message) == tm11.PollFulfillmentRequest
    assert message.collection_name == POLL_COLLECTION
    assert message.result_part_number == 2


@httpretty.activate
def test_poll_with_content_bindings():

    register_uri(POLL_URI, POLL_RESPONSE_WITH_MORE_1)

    client = create_client_11()

    gen = client.poll(POLL_COLLECTION, uri=POLL_PATH,
            content_bindings=[CONTENT_BINDING])

    block_1 = next(gen)
    print gen, block_1.content, CONTENT_BLOCKS
    assert block_1.content == CONTENT_BLOCKS[0]

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
    assert block_1.content == CONTENT_BLOCKS[0]

    message = get_sent_message()
    assert type(message) == tm11.PollRequest

    poll_params = message.poll_parameters
    assert len(poll_params.content_bindings) == 1
    assert poll_params.content_bindings[0].binding_id == binding.id
    assert poll_params.content_bindings[0].subtype_ids == binding.subtypes


@httpretty.activate
def test_subscribe():

    register_uri(COLLECTION_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)

    client = create_client_11()
    response = client.subscribe(POLL_COLLECTION, uri=COLLECTION_MANAGEMENT_PATH)

    assert response.collection_name == POLL_COLLECTION

    message = get_sent_message()
    assert type(message) == tm11.ManageCollectionSubscriptionRequest
    assert message.collection_name == POLL_COLLECTION
    assert message.action == tm11.ACT_SUBSCRIBE


@httpretty.activate
def test_subscribe_with_push():

    register_uri(COLLECTION_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)
    register_uri(DISCOVERY_URI_HTTP, DISCOVERY_RESPONSE)

    client = create_client_11(discovery_path=DISCOVERY_PATH)

    services = client.discover_services()

    inbox = next(ifilter(lambda s: s.type == SVC_INBOX, services))

    response = client.subscribe(POLL_COLLECTION, inbox_service=inbox, uri=COLLECTION_MANAGEMENT_PATH)

    assert response.collection_name == POLL_COLLECTION

    message = get_sent_message()
    assert type(message) == tm11.ManageCollectionSubscriptionRequest
    assert message.collection_name == POLL_COLLECTION
    assert message.push_parameters.inbox_address == inbox.address
    assert message.action == tm11.ACT_SUBSCRIBE



@httpretty.activate
def test_subscribtion_status():

    register_uri(COLLECTION_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)

    client = create_client_11()

    response = client.get_subscription_status(POLL_COLLECTION, subscription_id=SUBSCRIPTION_ID,
            uri=COLLECTION_MANAGEMENT_PATH)

    assert response.collection_name == POLL_COLLECTION

    message = get_sent_message()
    assert type(message) == tm11.ManageCollectionSubscriptionRequest
    assert message.collection_name == POLL_COLLECTION
    assert message.action == tm11.ACT_STATUS


@httpretty.activate
def test_unsubscribe():

    register_uri(COLLECTION_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)

    client = create_client_11()

    response = client.unsubscribe(POLL_COLLECTION, subscription_id=SUBSCRIPTION_ID,
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


@httpretty.activate
def test_pause_subscription():

    register_uri(COLLECTION_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)

    client = create_client_11()

    response = client.pause_subscription(POLL_COLLECTION, subscription_id=SUBSCRIPTION_ID,
            uri=COLLECTION_MANAGEMENT_PATH)

    assert response.collection_name == POLL_COLLECTION

    message = get_sent_message()
    assert type(message) == tm11.ManageCollectionSubscriptionRequest
    assert message.collection_name == POLL_COLLECTION
    assert message.action == tm11.ACT_PAUSE


@httpretty.activate
def test_resume_subscription():

    register_uri(COLLECTION_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)

    client = create_client_11()

    response = client.resume_subscription(POLL_COLLECTION, subscription_id=SUBSCRIPTION_ID,
            uri=COLLECTION_MANAGEMENT_PATH)

    assert response.collection_name == POLL_COLLECTION

    message = get_sent_message()
    assert type(message) == tm11.ManageCollectionSubscriptionRequest
    assert message.collection_name == POLL_COLLECTION
    assert message.action == tm11.ACT_RESUME


@httpretty.activate
def test_push():

    register_uri(INBOX_URI, INBOX_RESPONSE)

    client = create_client_11()

    response = client.push(CONTENT, CONTENT_BINDING, uri=INBOX_URI)

    message = get_sent_message()

    assert type(message) == tm11.InboxMessage
    assert len(message.content_blocks) == 1
    assert message.content_blocks[0].content == CONTENT 
    assert message.content_blocks[0].content_binding.binding_id == CONTENT_BINDING


@httpretty.activate
def test_push_with_destination():

    register_uri(INBOX_URI, INBOX_RESPONSE)

    client = create_client_11()
    dest_collections = [POLL_COLLECTION]

    response = client.push(CONTENT, CONTENT_BINDING, collections_names=dest_collections, uri=INBOX_URI)

    message = get_sent_message()

    assert type(message) == tm11.InboxMessage
    assert len(message.content_blocks) == 1
    assert message.content_blocks[0].content == CONTENT 
    assert message.content_blocks[0].content_binding.binding_id == CONTENT_BINDING

    assert message.destination_collection_names == dest_collections


