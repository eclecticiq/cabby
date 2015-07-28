from __future__ import absolute_import
from __future__ import print_function
from itertools import ifilter

import httpretty
import pytest
import urllib2
import json

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
    client = create_client(
        get_fix(version).HOST,
        version=("1.1" if version == 11 else "1.0"),
        **kwargs)
    return client


def register_uri(uri, body, version, **kwargs):
    content_type = VID_TAXII_XML_11 if version == 11 else VID_TAXII_XML_10
    httpretty.register_uri(httpretty.POST, uri, body=body, content_type='application/xml',
            adding_headers={'X-TAXII-Content-Type': content_type}, **kwargs)


def get_sent_message(version):
    body = httpretty.last_request().body
    return (tm11 if version == 11 else tm10).get_message_from_xml(body)


# Tests


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
    httpretty.reset()


@pytest.mark.parametrize("version", [11, 10])
def test_invalid_response(version):

    httpretty.enable()

    uri = get_fix(version).DISCOVERY_URI_HTTP

    httpretty.register_uri(httpretty.POST, uri, body="INVALID-BODY",
                           content_type='text/html')

    client = make_client(version)

    with pytest.raises(exc.InvalidResponseError):
        services = client.discover_services(uri=uri)

    httpretty.disable()
    httpretty.reset()


@pytest.mark.parametrize("version", [11, 10])
def test_invalid_response(version):

    httpretty.enable()

    jwt_path = '/management/auth/'
    jwt_url = 'http://{}{}'.format(get_fix(version).HOST, jwt_path)

    token = 'dummy'
    username = 'dummy-username'
    password = 'dummy-password'

    discovery_uri=get_fix(version).DISCOVERY_URI_HTTP

    register_uri(
        discovery_uri,
        get_fix(version).DISCOVERY_RESPONSE,
        version)
    print(version, get_fix(version).DISCOVERY_RESPONSE)

    def jwt_request_callback(request, uri, headers):
        body = json.loads(request.body)

        assert body['username'] == username
        assert body['password'] == password

        return 200, headers, json.dumps({'token': token})

    httpretty.register_uri(
        httpretty.POST,
        jwt_url,
        body=jwt_request_callback,
        content_type='application/json'
    )

    # client with relative JWT auth path
    client = make_client(version)
    client.set_auth(
        username=username,
        password=password,
        jwt_auth_url=jwt_path
    )
    services = client.discover_services(uri=discovery_uri)
    assert len(services) == 4

    # client with full JWT auth path
    client = make_client(version)
    client.set_auth(
        username=username,
        password=password,
        jwt_auth_url=jwt_url
    )
    services = client.discover_services(uri=discovery_uri)
    assert len(services) == 4

    httpretty.disable()
    httpretty.reset()
