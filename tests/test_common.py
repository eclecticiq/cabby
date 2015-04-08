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

import fixtures11
import fixtures10

CUSTOM_HEADER_NAME = 'X-custom-header'
CUSTOM_HEADER_VALUE = 'header value with space!'


def get_fix(version):
    return (fixtures10 if version == 10 else fixtures11)

def make_client(version, **kwargs):
    client = create_client(get_fix(version).HOST, version=("1.1" if version == 11 else "1.0"), **kwargs)
    return client


def register_uri(uri, body, version, **kwargs):
    content_type = VID_TAXII_XML_11 if version == 11 else VID_TAXII_XML_10
    httpretty.register_uri(httpretty.POST, uri, body=body, content_type='application/xml',
            adding_headers={'X-TAXII-Content-Type': content_type}, **kwargs)


def get_sent_message(version):
    body = httpretty.last_request().body
    return (tm11 if version == 11 else tm10).get_message_from_xml(body)


### Tests

@pytest.mark.parametrize("version", [11, 10])
def test_set_headers(version):

    httpretty.enable()

    uri = get_fix(version).DISCOVERY_URI_HTTP
    response = get_fix(version).DISCOVERY_RESPONSE

    register_uri(uri, response, version)

    client = make_client(version, headers={CUSTOM_HEADER_NAME : CUSTOM_HEADER_VALUE})

    services = client.discover_services(uri=uri)

    assert len(services) == 4

    message = get_sent_message(version)
    assert type(message) == (tm11 if version == 11 else tm10).DiscoveryRequest

    last_request = httpretty.last_request()

    assert CUSTOM_HEADER_NAME in last_request.headers
    assert last_request.headers[CUSTOM_HEADER_NAME] == CUSTOM_HEADER_VALUE

    httpretty.disable()



@pytest.mark.parametrize("version", [11, 10])
def test_invalid_response(version):

    httpretty.enable()

    uri = get_fix(version).DISCOVERY_URI_HTTP

    httpretty.register_uri(httpretty.POST, uri, body="INVALID-BODY", content_type='text/html')

    client = make_client(version)

    with pytest.raises(exc.InvalidResponseError):
        services = client.discover_services(uri=uri)

    httpretty.disable()

