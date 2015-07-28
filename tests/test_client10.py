

import pytest
import httpretty

from libtaxii import messages_10 as tm10
from libtaxii.constants import *

from cabby import create_client
from cabby import exceptions as exc
from cabby import entities

from fixtures10 import *


# Utils


def create_client_10(**kwargs):
    client = create_client(HOST, version="1.0", **kwargs)
    return client


def register_uri(uri, body, **kwargs):
    httpretty.register_uri(
        httpretty.POST, uri, body=body,
        content_type='application/xml',
        adding_headers={
            'X-TAXII-Content-Type': VID_TAXII_XML_10
        },
        **kwargs)


def get_sent_message():
    body = httpretty.last_request().body
    print(body)
    return tm10.get_message_from_xml(body)

# Tests


def test_no_discovery_path():
    client = create_client_10()

    with pytest.raises(exc.NoURIProvidedError):
        client.discover_services()


def test_no_discovery_path_when_pushing():
    client = create_client_10()

    with pytest.raises(exc.NoURIProvidedError):
        client.push(CONTENT, CONTENT_BINDING)


@httpretty.activate
def test_incorrect_path():

    httpretty.register_uri(httpretty.POST, DISCOVERY_URI_HTTP, status=404)

    client = create_client_10(discovery_path=DISCOVERY_PATH)

    with pytest.raises(exc.HTTPError):
        client.discover_services()


@httpretty.activate
def test_discovery():

    register_uri(DISCOVERY_URI_HTTP, DISCOVERY_RESPONSE)

    client = create_client_10(discovery_path=DISCOVERY_PATH)

    services = client.discover_services()

    assert len(services) == 4

    assert len([s for s in services if s.type == SVC_INBOX]) == 1
    assert len([s for s in services if s.type == SVC_DISCOVERY]) == 2

    message = get_sent_message()

    assert type(message) == tm10.DiscoveryRequest


@httpretty.activate
def test_discovery_https():

    register_uri(DISCOVERY_URI_HTTPS, DISCOVERY_RESPONSE)

    client = create_client_10(discovery_path=DISCOVERY_PATH, use_https=True)

    services = client.discover_services()

    assert len(services) == 4

    message = get_sent_message()
    assert type(message) == tm10.DiscoveryRequest


@httpretty.activate
def test_collections():

    register_uri(FEED_MANAGEMENT_URI, FEED_MANAGEMENT_RESPONSE)

    client = create_client_10()

    collections = client.get_collections(uri=FEED_MANAGEMENT_PATH)

    assert len(collections) == 2
    assert all(c.type == entities.Collection.TYPE_FEED for c in collections)

    feed = collections[0]

    assert len(feed.polling_services) == 1

    service = feed.polling_services[0]

    assert service.address == POLL_URI
    assert service.protocol is not None
    assert len(service.message_bindings) == 1

    message = get_sent_message()
    assert type(message) == tm10.FeedInformationRequest


@httpretty.activate
def test_collections_with_automatic_discovery():

    register_uri(DISCOVERY_URI_HTTP, DISCOVERY_RESPONSE)
    register_uri(FEED_MANAGEMENT_URI, FEED_MANAGEMENT_RESPONSE)

    client = create_client_10(discovery_path=DISCOVERY_URI_HTTP)

    collections = client.get_collections()

    assert len(collections) == 2

    message = get_sent_message()
    assert type(message) == tm10.FeedInformationRequest


@httpretty.activate
def test_poll():

    register_uri(POLL_URI, POLL_RESPONSE)

    client = create_client_10()
    blocks = list(client.poll(POLL_FEED, uri=POLL_PATH))

    assert len(blocks) == 2

    message = get_sent_message()
    assert type(message) == tm10.PollRequest
    assert message.feed_name == POLL_FEED


@httpretty.activate
def test_poll_with_subscription():

    register_uri(POLL_URI, POLL_RESPONSE)

    client = create_client_10()
    blocks = list(client.poll(POLL_FEED,
                              subscription_id=SUBSCRIPTION_ID,
                              uri=POLL_PATH))

    assert len(blocks) == 2

    message = get_sent_message()
    assert type(message) == tm10.PollRequest
    assert message.feed_name == POLL_FEED
    assert message.subscription_id == SUBSCRIPTION_ID


@httpretty.activate
def test_poll_with_content_bindings():

    register_uri(POLL_URI, POLL_RESPONSE)

    client = create_client_10()

    gen = client.poll(POLL_FEED, uri=POLL_PATH,
            content_bindings=[CONTENT_BINDING])

    block_1 = next(gen)
    print(gen, block_1.content, CONTENT_BLOCKS)
    assert block_1.content == CONTENT_BLOCKS[0]

    message = get_sent_message()
    assert type(message) == tm10.PollRequest
    assert message.feed_name == POLL_FEED

    assert len(message.content_bindings) == 1
    assert message.content_bindings[0] == CONTENT_BINDING

    binding = entities.ContentBinding(CONTENT_BINDING, subtypes=['substype-a'])
    gen = client.poll(POLL_FEED, uri=POLL_PATH,
            content_bindings=[binding])

    block_1 = next(gen)
    assert block_1.content == CONTENT_BLOCKS[0]

    message = get_sent_message()
    assert type(message) == tm10.PollRequest

    assert len(message.content_bindings) == 1
    assert message.content_bindings[0] == binding.id



@httpretty.activate
def test_subscribe():

    register_uri(FEED_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)

    client = create_client_10()

    response = client.subscribe(POLL_FEED, uri=FEED_MANAGEMENT_PATH)

    assert response.collection_name == POLL_FEED
    assert len(response.subscriptions) == 1

    subscription = response.subscriptions[0]
    assert subscription.status == subscription.STATUS_UNKNOWN

    message = get_sent_message()
    assert type(message) == tm10.ManageFeedSubscriptionRequest
    assert message.feed_name == POLL_FEED
    assert message.action == tm10.ACT_SUBSCRIBE


@httpretty.activate
def test_subscribe_with_push():

    register_uri(DISCOVERY_URI_HTTP, DISCOVERY_RESPONSE)
    register_uri(FEED_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)

    client = create_client_10(discovery_path=DISCOVERY_PATH)

    services = client.discover_services()

    inbox = next((s for s in services if s.type == SVC_INBOX), None)

    response = client.subscribe(POLL_FEED, inbox_service=inbox,
                                uri=FEED_MANAGEMENT_PATH)

    assert response.collection_name == POLL_FEED
    assert len(response.subscriptions) == 1

    subscription = response.subscriptions[0]
    # TAXII 1.0 reply lacks 'status' field
    assert subscription.status == subscription.STATUS_UNKNOWN

    message = get_sent_message()
    assert type(message) == tm10.ManageFeedSubscriptionRequest
    assert message.feed_name == POLL_FEED
    assert message.delivery_parameters.inbox_address == inbox.address
    assert message.action == tm10.ACT_SUBSCRIBE


@httpretty.activate
def test_unsubscribe():

    register_uri(FEED_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)

    client = create_client_10()

    response = client.unsubscribe(POLL_FEED,
                                  SUBSCRIPTION_ID,
                                  uri=FEED_MANAGEMENT_PATH)

    assert response.collection_name == POLL_FEED
    assert len(response.subscriptions) == 1
    # TAXII 1.0 does not reply with 'status' field configured
    assert response.subscriptions[0].status == \
        entities.Subscription.STATUS_UNKNOWN

    message = get_sent_message()
    assert type(message) == tm10.ManageFeedSubscriptionRequest
    assert message.feed_name == POLL_FEED
    assert message.action == tm10.ACT_UNSUBSCRIBE


@httpretty.activate
def test_push():

    register_uri(INBOX_URI, INBOX_RESPONSE)

    client = create_client_10()

    response = client.push(CONTENT, CONTENT_BINDING, uri=INBOX_URI)

    message = get_sent_message()

    assert type(message) == tm10.InboxMessage
    assert len(message.content_blocks) == 1
    assert message.content_blocks[0].content == CONTENT
    assert message.content_blocks[0].content_binding == CONTENT_BINDING
