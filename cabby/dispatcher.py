from collections import namedtuple
import os
import ssl
import sys
import logging

from six import StringIO

import furl
import gzip
import requests
from lxml import etree
from six.moves import urllib
from requests.auth import AuthBase, HTTPBasicAuth

from libtaxii import messages_11 as tm11
from libtaxii import messages_10 as tm10

from . import constants as const
from ._version import __version__ as cabby_version

from .exceptions import (
    UnsuccessfulStatusError, HTTPError, InvalidResponseError)


log = logging.getLogger(__name__)


def raise_http_error(status_code, response_stream=None):
    if log.isEnabledFor(logging.DEBUG) and response_stream:
        body = response_stream.read()
        log.debug("Response:\n%s", body.decode('utf-8'))
    raise HTTPError(status_code)


def send_taxii_request(session, url, request, taxii_binding=None,
                       tls_details=None, timeout=None):
    '''
    Send XML message to a TAXII service and parse a response.
    '''

    log.info("Sending {} to {}".format(request.message_type, url))

    request_body = request.to_xml(pretty_print=True)

    log.debug("Request:\n%s", request_body.decode('utf-8'))

    session = get_taxii_session(
        session,
        url_scheme=furl.furl(url).scheme,
        message_binding=taxii_binding)

    if tls_details and tls_details.get('key_password'):
        # Workaround until
        # https://github.com/kennethreitz/requests/issues/2519 is fixed
        try:
            response = get_response_using_key_pass(
                url, request_body, session, timeout=timeout, **tls_details)
        except urllib.error.HTTPError as e:
            log.error(
                "Error while connecting to {}".format(url),
                exc_info=True)
            raise_http_error(e.getcode())

        stream, headers = response, response.headers
    else:
        response = session.post(url, data=request_body, stream=True,
                                timeout=timeout)
        if not response.ok:
            raise_http_error(response.status_code, response.raw)

        stream, headers = response.raw, response.headers

    if 'gzip' in headers.get('content-encoding', ''):

        if sys.version_info < (3, 2):
            # It is impossible to seek on a HTTP response inside gzipped stream
            # in gzip lib for python < v3.2, so we are forced to read all
            # stream content into memory
            stream = StringIO(stream.read())

        stream = gzip.GzipFile(fileobj=stream)

    gen = _parse_response(stream, headers, version=request.version)
    obj = next(gen)

    if obj == const.STREAM_MARKER:
        return gen
    elif hasattr(obj, 'status_type'):
        if obj.status_type != 'SUCCESS':
            raise UnsuccessfulStatusError(obj)
        else:
            return None
    return obj


def _cleanup_batch(curr_elem, batch):
    current_parent = curr_elem.getparent()

    for elem in batch:
        if elem.getparent() is not None:
            parent = elem.getparent()
        else:
            parent = current_parent
        parent.remove(elem)

    del batch[:]


def _stream_poll_response(namespace, stream):

    module = const.MODULES[namespace]

    response_cls = const.MODULES[namespace].PollResponse

    batch_max_size = 3
    to_delete_batch = []

    for action, elem in stream:
        if action == 'end':
            tag = elem.xpath('local-name()')

            # If current element is ContentBlock
            if tag == module.ContentBlock.NAME:
                obj = module.ContentBlock.from_etree(elem)

            # If current element is PollResponse
            # meaning that this is a last one
            elif tag == response_cls.message_type:
                _cleanup_batch(elem, to_delete_batch)
                obj = response_cls.from_etree(elem)
            else:
                continue

            if log.isEnabledFor(logging.DEBUG):
                log.debug("Stream element:\n{}"
                          .format(etree.tostring(elem).decode('utf-8')))

            yield obj

            # Cleaning up element to free up memory
            elem.clear()

            # Removing all elements from a batch if it is time
            if len(to_delete_batch) >= batch_max_size:
                _cleanup_batch(elem, to_delete_batch)

            # Postponing removal of the element from a tree
            # to avoid memory corruption (libxml2 crashes)
            to_delete_batch.append(elem)


def _parse_response(stream, headers, version):

    content_type = headers.get('X-TAXII-Content-Type')

    if not content_type:
        body = stream.read()
        headers = '\n'.join([
            '{}={}'.format(k, v) for k, v in headers.items()])
        log.debug(
            "Invalid response:\n{}\n{}".format(headers, body))
        raise InvalidResponseError("Invalid response received")

    elif content_type not in const.SUPPORTED_CONTENT_BINDINGS:
        raise ValueError('Unsupported X-TAXII-Content-Type: {}'
                         .format(content_type))
    elif content_type == const.CERT_EU_JSON_10_BINDING:
        body = stream.read()
        yield tm10.get_message_from_json(body)

    support_huge_trees = not os.environ.get('CABBY_NO_HUGE_TREES')
    gen = etree.iterparse(
        stream,
        events=('start', 'end'),
        # inject default attributes from DTD or XMLSchema
        attribute_defaults=False,
        # validate against a DTD referenced by the document
        dtd_validation=False,
        # use DTD for parsing
        load_dtd=False,
        # prevent network access for related files (default: True)
        no_network=True,
        # try hard to parse through broken XML
        recover=False,
        # discard blank text nodes that appear ignorable
        remove_blank_text=False,
        # discard comments
        remove_comments=False,
        # discard processing instructions
        remove_pis=False,
        # replace CDATA sections by normal text content (default: True)
        strip_cdata=True,
        # save memory for short text content (default: True)
        compact=True,
        # replace entities by their text value (default: True)
        resolve_entities=False,
        # enable/disable security restrictions and support very deep
        # trees and very long text content
        huge_tree=support_huge_trees)

    action, root = next(gen)
    namespace = etree.QName(root).namespace
    message_type = root.xpath('local-name()')

    if namespace not in const.VERSIONS:
        raise ValueError(
            'Unsupported namespace: {}'.format(namespace))
    elif version != const.VERSIONS[namespace]:
        raise InvalidResponseError(
            "Response TAXII version '{}' "
            "does not match request version '{}'"
            .format(const.VERSIONS[namespace], version))

    if message_type in [tm11.PollResponse.message_type,
                        tm10.PollResponse.message_type]:

        yield const.STREAM_MARKER

        for obj in _stream_poll_response(namespace, gen):
            yield obj

    else:
        # Walk tree iterator to the end to fill up root element
        for _ in gen:
            pass

        if log.isEnabledFor(logging.DEBUG):
            log.debug("Response:\n%s",
                      etree.tostring(root, pretty_print=True).decode('utf-8'))

        yield _parse_full_tree(content_type, message_type, root)


def _parse_full_tree(content_type, message_type, elem):

    if content_type == const.XML_10_BINDING:
        tm = tm10
    elif content_type == const.XML_11_BINDING:
        tm = tm11
    else:
        raise ValueError(
            "Unsupported content type binding {}".format(content_type))

    if message_type == const.MSG_DISCOVERY_REQUEST:
        return tm.DiscoveryRequest.from_etree(elem)
    elif message_type == const.MSG_DISCOVERY_RESPONSE:
        return tm.DiscoveryResponse.from_etree(elem)
    elif message_type == const.MSG_POLL_REQUEST:
        return tm.PollRequest.from_etree(elem)
    elif message_type == const.MSG_POLL_RESPONSE:
        return tm.PollResponse.from_etree(elem)
    elif message_type == const.MSG_STATUS_MESSAGE:
        return tm.StatusMessage.from_etree(elem)
    elif message_type == const.MSG_INBOX_MESSAGE:
        return tm.InboxMessage.from_etree(elem)

    if tm == tm11:
        # TAXII 1.1 specific
        if message_type == const.MSG_COLLECTION_INFORMATION_REQUEST:
            return tm.CollectionInformationRequest.from_etree(elem)
        elif message_type == const.MSG_COLLECTION_INFORMATION_RESPONSE:
            return tm.CollectionInformationResponse.from_etree(elem)
        elif message_type == const.MSG_MANAGE_COLLECTION_SUBSCRIPTION_REQUEST:
            return tm.ManageCollectionSubscriptionRequest.from_etree(elem)
        elif message_type == const.MSG_MANAGE_COLLECTION_SUBSCRIPTION_RESPONSE:
            return tm.ManageCollectionSubscriptionResponse.from_etree(elem)
        elif message_type == const.MSG_POLL_FULFILLMENT_REQUEST:
            return tm.PollFulfillmentRequest.from_etree(elem)
    elif tm == tm10:
        # TAXII 1.0 specific
        if message_type == const.MSG_FEED_INFORMATION_REQUEST:
            return tm.FeedInformationRequest.from_etree(elem)
        elif message_type == const.MSG_FEED_INFORMATION_RESPONSE:
            return tm.FeedInformationResponse.from_etree(elem)
        elif message_type == const.MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST:
            return tm.ManageFeedSubscriptionRequest.from_etree(elem)
        elif message_type == const.MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE:
            return tm.ManageFeedSubscriptionResponse.from_etree(elem)

    raise ValueError('Unknown message_type: %s' % message_type)


class JWTAuth(AuthBase):

    """Attaches JWT Authentication to the given Request object."""
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer {}'.format(self.token)
        return r


def get_generic_session(proxies=None, headers=None,
                        username=None, password=None,
                        cert_file=None, key_file=None,
                        verify_ssl=True):

    session = requests.Session()
    session.verify = verify_ssl

    if proxies:
        session.proxies = proxies

    if headers:
        session.headers.update(headers)

    if username and password:
        session.auth = HTTPBasicAuth(username, password)

    session.headers['User-Agent'] = 'Cabby {}'.format(cabby_version)

    if cert_file and key_file:
        session.cert = (cert_file, key_file)

    return session


def set_jwt_token(session, jwt_token):
    session.auth = JWTAuth(jwt_token)
    return session


def get_taxii_session(session, url_scheme='https', content_type=None,
                      message_binding=const.XML_11_BINDING,
                      service_binding=None):

    if not content_type:
        if message_binding not in const.BINDINGS_TO_CONTENT_TYPE:
            raise ValueError('No content type provided')
        content_type = const.BINDINGS_TO_CONTENT_TYPE[message_binding]

    if not service_binding:
        if message_binding not in const.BINDINGS_TO_SERVICES:
            raise ValueError('No service binding provided')
        service_bindings = const.BINDINGS_TO_SERVICES[message_binding]

    if url_scheme not in const.SCHEMA_TO_PROTOCOL_BINDINGS:
        raise ValueError(
            'No known protocol bindings for scheme {}'.format(url_scheme))

    session.headers.update({
        'Content-Type': content_type,
        'Accept': content_type,
        'X-TAXII-Content-Type': message_binding,
        'X-TAXII-Accept': message_binding,
        'X-TAXII-Services': service_bindings,
        'X-TAXII-Protocol': const.SCHEMA_TO_PROTOCOL_BINDINGS[url_scheme]
    })
    return session


def obtain_jwt_token(session, jwt_url, username, password):
    log.info("Obtaining JWT token from {}".format(jwt_url))

    response = session.post(jwt_url, json={
        'username': username,
        'password': password
    })

    if not response.ok:
        raise_http_error(response.status_code, response.raw)

    body = response.json()
    if 'token' not in body:
        log.debug("Incorrect JWT response:\n{}".format(body))
        raise ValueError("No token found in JWT auth response")
    return body['token']


def get_response_using_key_pass(url, data, session, cert_file, key_file,
                                key_password, ca_cert=None, timeout=None):

    if sys.version_info < (2, 7, 9):
        raise ValueError(
            'Key password specification is not supported in Python < v2.7.9')

    if session.auth:
        # Using Requests Session's auth handlers to fill in proper headers
        DummyRequest = namedtuple('DummyRequest', ['headers'])
        headers = session.auth(DummyRequest(headers=session.headers)).headers
    else:
        headers = session.headers

    context = ssl.create_default_context(
        ssl.Purpose.CLIENT_AUTH, cafile=ca_cert)

    context.load_cert_chain(cert_file, key_file, password=key_password)

    if not session.verify and not ca_cert:
        context.verify_mode = ssl.CERT_NONE
    elif session.verify:
        context.verify_mode = ssl.CERT_REQUIRED

        if not ca_cert:
            context.set_default_verify_paths()

    handlers = [urllib.request.HTTPSHandler(context=context)]

    if session.proxies:
        handlers.append(
            urllib.request.ProxyHandler(session.proxies))

    opener = urllib.request.build_opener(*handlers)

    request = urllib.request.Request(url, data, headers)

    if timeout:
        return opener.open(request, timeout=timeout)
    else:
        return opener.open(request)
