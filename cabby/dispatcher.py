from collections import namedtuple
import logging
import ssl
import sys

import furl
import requests
from lxml import etree
from six.moves import urllib
from requests.auth import AuthBase, HTTPBasicAuth

from libtaxii import messages_11 as tm11
from libtaxii import messages_10 as tm10
from libtaxii import constants as const

from .exceptions import (
    UnsuccessfulStatusError, HTTPError, InvalidResponseError
)


STREAM_MARKER = 'STREAM'

VERSIONS = {
    const.NS_MAP['taxii_11']: const.VID_TAXII_XML_11,
    const.NS_MAP['taxii']: const.VID_TAXII_XML_10
}

MODULES = {
    const.NS_MAP['taxii_11']: tm11,
    const.NS_MAP['taxii']: tm10
}

BINDINGS_TO_CONTENT_TYPE = {
    const.VID_TAXII_XML_10: 'application/xml',
    const.VID_TAXII_XML_11: 'application/xml',
    const.VID_CERT_EU_JSON_10: 'application/json'
}

BINDINGS_TO_SERVICES = {
    const.VID_TAXII_XML_10: const.VID_TAXII_SERVICES_10,
    const.VID_TAXII_XML_11: const.VID_TAXII_SERVICES_11,
    const.VID_CERT_EU_JSON_10: const.VID_TAXII_SERVICES_10
}


log = logging.getLogger(__name__)


def raise_http_error(status_code, response_stream):

    if log.isEnabledFor(logging.DEBUG):
        body = response_stream.read()
        log.debug("Response:\n%s", body.decode('utf-8'))

    raise HTTPError(status_code)


def if_key_encrypted(key_file):
    with open(key_file, 'r') as f:
        return 'Proc-Type: 4,ENCRYPTED' in f.read()


def send_taxii_request(url, request, headers=None, proxies=None, ca_cert=None,
                       tls_auth=None, jwt_url=None, username=None,
                       password=None, verify_ssl=True):
    '''Send TAXII XML message to a service and parse response'''

    log.info("Sending %s to %s", request.message_type, url)
    request_body = request.to_xml(pretty_print=True)
    log.debug("Request:\n%s", request_body.decode('utf-8'))

    headers = (headers or {})
    headers.update({
        'X-TAXII-Protocol': (
            const.VID_TAXII_HTTPS_10 if furl.furl(url).scheme == 'https'
            else const.VID_TAXII_HTTP_10)
    })

    if not tls_auth:
        cert_file = None
        key_file = None
        key_password = None
    elif len(tls_auth) == 2:
        cert_file, key_file = tls_auth
        key_password = None
    elif len(tls_auth) == 3:
        cert_file, key_file, key_password = tls_auth
    else:
        raise ValueError('`tls_auth` is either None,'
                         ' or (cert_file, key_file)'
                         ' or (cert_file, key_file, key_password)')

    if key_file and not key_password and if_key_encrypted(key_file):
        raise ValueError(
            'Key file is encrypted but key password was not provided')

    session_context = get_session(
        message_binding=request.version,
        proxies=proxies,
        username=username,
        password=password,
        jwt_url=jwt_url,
        cert_file=cert_file,
        key_file=key_file,
        verify_ssl=(ca_cert or verify_ssl),
    )

    with session_context as session:
        if key_password:
            # Workaround until
            # https://github.com/kennethreitz/requests/issues/2519 is fixed
            try:
                response = get_response_using_key_pass(
                    url, request_body, session,
                    cert_file, key_file, key_password,
                    ca_cert=ca_cert)
            except urllib.error.HTTPError as e:
                raise_http_error(e.getcode(), response)

            stream, headers = response, response.headers
        else:
            response = session.post(
                url, data=request_body, headers=headers, stream=True)

            if not response.ok:
                raise_http_error(response.status_code, response.raw)

            stream, headers = response.raw, response.headers

    log.info("Response received for %s from %s", request.message_type, url)

    gen = _parse_response(stream, headers, version=request.version)
    obj = next(gen)

    if obj == STREAM_MARKER:
        return gen
    elif hasattr(obj, 'status_type'):
        if obj.status_type != const.ST_SUCCESS:
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

    module = MODULES[namespace]

    block_cls = module.ContentBlock
    response_cls = MODULES[namespace].PollResponse

    batch_max_size = 3
    to_delete_batch = []

    for action, elem in stream:
        if action == 'end':
            tag = elem.xpath('local-name()')

            # If current element is ContentBlock
            if tag == block_cls.NAME:
                obj = block_cls.from_etree(elem)

            # If current element is PollResponse
            # meaning that this is a last one
            elif tag == response_cls.message_type:
                _cleanup_batch(elem, to_delete_batch)
                obj = response_cls.from_etree(elem)
            else:
                continue

            if log.isEnabledFor(logging.DEBUG):
                log.debug("Stream element:\n%s",
                          etree.tostring(elem).decode('utf-8'))

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
            "Invalid response:\n%s\n%s",
            headers,
            body)
        raise InvalidResponseError("Invalid response received")

    elif content_type not in [const.VID_TAXII_XML_10,
                              const.VID_TAXII_XML_11,
                              const.VID_CERT_EU_JSON_10]:
        raise ValueError('Unsupported X-TAXII-Content-Type: {}'
                         .format(content_type))
    elif content_type == const.VID_CERT_EU_JSON_10:
        body = stream.read()
        yield tm10.get_message_from_json(body)

    gen = etree.iterparse(stream, events=('start', 'end'))

    action, root = next(gen)
    namespace = etree.QName(root).namespace
    message_type = root.xpath('local-name()')

    if namespace not in VERSIONS:
        raise ValueError('Unsupported namespace: {}'
                         .format(namespace))
    elif version != VERSIONS[namespace]:
        raise InvalidResponseError(
            "Response TAXII version '%s' "
            "does not match request version '%s'" %
            (VERSIONS[namespace], version))

    if message_type in [tm11.PollResponse.message_type,
                        tm10.PollResponse.message_type]:

        yield STREAM_MARKER

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

    if content_type == const.VID_TAXII_XML_10:
        tm = tm10
    elif content_type == const.VID_TAXII_XML_11:
        tm = tm11
    else:
        raise ValueError("Unsupported content type {}" .format(content_type))

    if tm == tm11 or tm == tm10:
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


def get_session(message_binding=const.VID_TAXII_XML_11, service_binding=None,
                proxies=None, headers=None, cert_file=None, key_file=None,
                content_type=None, username=None, password=None, jwt_url=None,
                verify_ssl=True):

    session = requests.Session()

    session.verify = verify_ssl

    if proxies:
        session.proxies = proxies

    if username and password:
        if jwt_url:
            token = obtain_jwt_token(
                jwt_url, username=username, password=password)
            session.auth = JWTAuth(token)
        else:
            session.auth = HTTPBasicAuth(username, password)

    if cert_file and key_file:
        session.cert = (cert_file, key_file)

    if not content_type:
        if message_binding not in BINDINGS_TO_CONTENT_TYPE:
            raise ValueError('No content type provided')

        content_type = BINDINGS_TO_CONTENT_TYPE[message_binding]

    if not service_binding:
        if message_binding not in BINDINGS_TO_SERVICES:
            raise ValueError('No service binding provided')

        service_bindings = BINDINGS_TO_SERVICES[message_binding]

    _headers = {
        'User-Agent': 'cabby',
        'Content-Type': content_type,
        'Accept': content_type,
        'X-TAXII-Content-Type': message_binding,
        'X-TAXII-Accept': message_binding,
        'X-TAXII-Services': service_bindings,
    }

    if headers:
        _headers.update(headers)

    session.headers.update(_headers)

    return session


def obtain_jwt_token(url, username, password):

    log.info("Obtaining JWT token from %s", url)

    r = requests.post(url, json={
        'username': username,
        'password': password
    })
    r.raise_for_status()
    body = r.json()

    if 'token' not in body:
        log.debug("Incorrect JWT response:\n%s", body)
        raise ValueError("No token in JWT auth response")

    return body['token']


def get_response_using_key_pass(url, data, session, cert_file, key_file,
                                key_password, ca_cert=None):

    if sys.version_info < (2, 7, 9):
        raise ValueError(
            'Key password specification is not supported in Python <2.7.9')

    # Using Requests Session's auth handlers to fill in proper headers
    DummyRequest = namedtuple('DummyRequest', ['headers'])
    headers = session.auth(DummyRequest(headers=session.headers)).headers

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

    return opener.open(request)
