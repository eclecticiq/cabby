import pytest
import urllib2
import httpretty

from itertools import ifilter

from libtaxii import messages_11 as tm11
from libtaxii import messages_10 as tm10
from libtaxii.constants import *

from cabby import create_client
from cabby import exceptions as exc
from cabby import entities

from fixtures11 import *

CUSTOM_HEADER_NAME = 'X-custom-header'
CUSTOM_HEADER_VALUE = 'header value with space!'

def make_client(version, **kwargs):
    client = create_client(HOST, version=("1.1" if version == 11 else "1.0"), **kwargs)
    return client


def register_uri(uri, body, **kwargs):
    httpretty.register_uri(httpretty.POST, uri, body=body, content_type='application/xml',
            adding_headers={'X-TAXII-Content-Type': VID_TAXII_XML_11}, **kwargs)


def get_sent_message(version):
    body = httpretty.last_request().body
    return (tm11 if version == 11 else tm10).get_message_from_xml(body)


### Tests

@pytest.mark.parametrize("version", [11, 10])
def test_set_headers(version):

    httpretty.enable()

    register_uri(DISCOVERY_URI_HTTP, DISCOVERY_RESPONSE)

    client = make_client(version, headers={CUSTOM_HEADER_NAME : CUSTOM_HEADER_VALUE})

    services = client.discover_services(uri=DISCOVERY_URI_HTTP)

    assert len(services) == 4

    message = get_sent_message(version)
    assert type(message) == (tm11 if version == 11 else tm10).DiscoveryRequest

    last_request = httpretty.last_request()

    assert CUSTOM_HEADER_NAME in last_request.headers
    assert last_request.headers[CUSTOM_HEADER_NAME] == CUSTOM_HEADER_VALUE

    httpretty.disable()
