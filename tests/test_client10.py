import pytest
import urllib2

import httpretty

from itertools import ifilter

from taxii_client import create_client
from taxii_client import exceptions as exc

from libtaxii import messages_10 as tm10
from libtaxii.constants import *
from fixtures10 import *


### Utils

def create_client_10(**kwargs):
    client = create_client(HOST, version="1.0", **kwargs)
    return client


def register_uri(uri, body, **kwargs):
    httpretty.register_uri(httpretty.POST, uri, body=body, content_type='application/xml',
            adding_headers={'X-TAXII-Content-Type': VID_TAXII_XML_10}, **kwargs)


def get_sent_message():
    body = httpretty.last_request().body
    return tm10.get_message_from_xml(body)

### Tests

def test_no_discovery_path():
    client = create_client_10()

    with pytest.raises(exc.NoURIProvidedError):
        client.discover_services()


def test_no_discovery_path_when_pushing():
    client = create_client_10()

    with pytest.raises(exc.NoURIProvidedError):
        client.push(CONTENT, CONTENT_BINDING)


def test_incorrect_path():

    httpretty.enable()
    httpretty.register_uri(httpretty.POST, DISCOVERY_URI_HTTP, status=404)

    client = create_client_10(discovery_path=DISCOVERY_PATH)

    with pytest.raises(exc.UnsuccessfulStatusError):
        client.discover_services()


def test_discovery():

    httpretty.enable()
    register_uri(DISCOVERY_URI_HTTP, DISCOVERY_RESPONSE)

    client = create_client_10(discovery_path=DISCOVERY_PATH)

    services = client.discover_services()

    assert len(services) == 4

    assert len(filter(lambda s: s.service_type == SVC_INBOX, services)) == 1
    assert len(filter(lambda s: s.service_type == SVC_DISCOVERY, services)) == 2

    message = get_sent_message()

    assert type(message) == tm10.DiscoveryRequest


def test_discovery_https():

    httpretty.enable()
    register_uri(DISCOVERY_URI_HTTPS, DISCOVERY_RESPONSE)

    client = create_client_10(discovery_path=DISCOVERY_PATH, use_https=True)

    services = client.discover_services()

    assert len(services) == 4

    message = get_sent_message()
    assert type(message) == tm10.DiscoveryRequest


def test_feeds():

    httpretty.enable()
    register_uri(FEED_MANAGEMENT_URI, FEED_MANAGEMENT_RESPONSE)

    client = create_client_10()

    response = client.get_feeds(uri=FEED_MANAGEMENT_PATH)

    assert len(response.feed_informations) == 2

    message = get_sent_message()
    assert type(message) == tm10.FeedInformationRequest


def test_collections_with_automatic_discovery():

    httpretty.enable()
    register_uri(DISCOVERY_URI_HTTP, DISCOVERY_RESPONSE)
    register_uri(FEED_MANAGEMENT_URI, FEED_MANAGEMENT_RESPONSE)

    client = create_client_10(discovery_path=DISCOVERY_URI_HTTP)

    response = client.get_feeds()

    assert len(response.feed_informations) == 2

    message = get_sent_message()
    assert type(message) == tm10.FeedInformationRequest


def test_poll():

    httpretty.enable()
    register_uri(POLL_URI, POLL_RESPONSE)

    client = create_client_10()
    blocks = list(client.poll(POLL_FEED, uri=POLL_PATH))

    assert len(blocks) == 2

    message = get_sent_message()
    assert type(message) == tm10.PollRequest
    assert message.feed_name == POLL_FEED


def test_poll_with_subscription():

    httpretty.enable()
    register_uri(POLL_URI, POLL_RESPONSE)

    client = create_client_10()
    blocks = list(client.poll(POLL_FEED, subscription_id=SUBSCRIPTION_ID, uri=POLL_PATH))

    assert len(blocks) == 2

    message = get_sent_message()
    assert type(message) == tm10.PollRequest
    assert message.feed_name == POLL_FEED
    assert message.subscription_id == SUBSCRIPTION_ID


def test_poll_prepared():

    httpretty.enable()
    register_uri(POLL_URI, POLL_RESPONSE)

    client = create_client_10()
    blocks = list(client.poll_prepared(POLL_FEED, uri=POLL_PATH))

    assert len(blocks) == 2

    assert blocks[0].source_collection == POLL_FEED

    assert blocks[0].content == CONTENT_BLOCKS[0]
    assert blocks[1].content == CONTENT_BLOCKS[1]

    message = get_sent_message()
    assert type(message) == tm10.PollRequest
    assert message.feed_name == POLL_FEED


def test_subscribe():

    httpretty.enable()
    register_uri(FEED_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)

    client = create_client_10()

    response = client.subscribe(POLL_FEED, uri=FEED_MANAGEMENT_PATH)

    assert response.feed_name == POLL_FEED

    message = get_sent_message()
    assert type(message) == tm10.ManageFeedSubscriptionRequest
    assert message.feed_name == POLL_FEED
    assert message.action == tm10.ACT_SUBSCRIBE


def test_subscribe_with_push():

    httpretty.enable()
    register_uri(DISCOVERY_URI_HTTP, DISCOVERY_RESPONSE)
    register_uri(FEED_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)

    client = create_client_10(discovery_path=DISCOVERY_PATH)

    services = client.discover_services()

    inbox = next(ifilter(lambda s: s.service_type == SVC_INBOX, services))

    response = client.subscribe(POLL_FEED, inbox_service=inbox, uri=FEED_MANAGEMENT_PATH)

    assert response.feed_name == POLL_FEED

    message = get_sent_message()
    assert type(message) == tm10.ManageFeedSubscriptionRequest
    assert message.feed_name == POLL_FEED
    assert message.delivery_parameters.inbox_address == inbox.service_address
    assert message.action == tm10.ACT_SUBSCRIBE


def test_unsubscribe():

    httpretty.enable()
    register_uri(FEED_MANAGEMENT_URI, SUBSCRIPTION_RESPONSE)

    client = create_client_10()

    response = client.unsubscribe(POLL_FEED, uri=FEED_MANAGEMENT_PATH)

    assert response.feed_name == POLL_FEED

    message = get_sent_message()
    assert type(message) == tm10.ManageFeedSubscriptionRequest
    assert message.feed_name == POLL_FEED
    assert message.action == tm10.ACT_UNSUBSCRIBE


def test_push():

    httpretty.enable()
    register_uri(INBOX_URI, INBOX_RESPONSE)

    client = create_client_10()

    response = client.push(CONTENT, CONTENT_BINDING, uri=INBOX_URI)

    message = get_sent_message()

    assert type(message) == tm10.InboxMessage
    assert len(message.content_blocks) == 1
    assert message.content_blocks[0].content == CONTENT 
    assert message.content_blocks[0].content_binding == CONTENT_BINDING


