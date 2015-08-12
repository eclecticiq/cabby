import logging

import requests
from furl import furl
from lxml import etree
from six.moves import urllib

from libtaxii.clients import HttpClient
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

log = logging.getLogger(__name__)


def _set_auth_details(tclient, cert_file=None, key_file=None,
                      username=None, password=None, is_jwt=False):
    tls_auth = (cert_file and key_file)
    basic_auth = (not is_jwt and username and password)

    credentials = None
    if tls_auth and basic_auth:
        tclient.set_auth_type(HttpClient.AUTH_CERT_BASIC)
        credentials = {
            'key_file': key_file,
            'cert_file': cert_file,
            'username': username,
            'password': password
        }
    elif tls_auth:
        tclient.set_auth_type(HttpClient.AUTH_CERT)
        credentials = {
            'key_file': key_file,
            'cert_file': cert_file,
        }
    elif basic_auth:
        tclient.set_auth_type(HttpClient.AUTH_BASIC)
        credentials = {
            'username': username,
            'password': password
        }

    if credentials:
        tclient.set_auth_credentials(credentials)

    return tclient


def _obtain_jwt_token(url, username, password):

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


def _extend_headers(headers, auth_details):

    jwt_url = auth_details.get('jwt_url_prepared')
    username = auth_details.get('username')
    password = auth_details.get('password')

    _headers = dict(headers)

    if jwt_url:
        token = _obtain_jwt_token(jwt_url,
                                  username=username,
                                  password=password)
        _headers['Authorization'] = 'Bearer {}'.format(token)

    return _headers


def send_taxii_request(url, request, headers, auth_details=None,
                       proxy_details=None):
    '''Send TAXII XML message to a service and parse response'''

    log.info("Sending %s to %s", request.message_type, url)
    request_body = request.to_xml(pretty_print=True)

    log.debug("Request:\n%s", request_body)

    headers = _extend_headers(headers, auth_details or {})

    fu = furl(url)

    tclient = HttpClient(use_https=(fu.scheme == 'https'))
    tclient = _set_auth_details(
        tclient,
        cert_file=auth_details.get('cert_file'),
        key_file=auth_details.get('key_file'),
        username=auth_details.get('username'),
        password=auth_details.get('password'),
        is_jwt=bool(auth_details.get('jwt_url'))
    )

    if proxy_details:
        tclient.set_proxy(**proxy_details)

    response_raw = tclient.call_taxii_service2(
        host=fu.host,
        path=str(fu.path),
        port=fu.port,
        get_params_dict=fu.query.params,
        message_binding=request.version,
        post_data=request_body,
        headers=headers
    )

    log.info("Response received for %s from %s", request.message_type, url)

    if isinstance(response_raw, urllib.error.URLError):
        desc = str(response_raw)
        body = response_raw.read()
        log.debug("%s: %s", desc, body)
        raise HTTPError(desc)

    gen = _parse_response(response_raw, version=request.version)
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
                log.debug("Stream element:\n%s", etree.tostring(elem))

            yield obj

            # Cleaning up element to free up memory
            elem.clear()

            # Removing all elements from a batch if it is time
            if len(to_delete_batch) >= batch_max_size:
                _cleanup_batch(elem, to_delete_batch)

            # Postponing removal of the element from a tree
            # to avoid memory corruption (libxml2 crashes)
            to_delete_batch.append(elem)


def _parse_response(response, version):

    try:
        content_type = response.info().getheader('X-TAXII-Content-Type')
    except AttributeError:
        # http.client.HTTPResponse
        content_type = response.getheader('X-TAXII-Content-Type')

    # https://github.com/TAXIIProject/libtaxii/issues/186
    if not content_type:
        headers = ''.join(response.info().headers)
        body = response.read()
        log.debug("Invalid response:\n%s\n%s", headers, body)
        raise InvalidResponseError("Invalid response received")

    elif content_type not in [const.VID_TAXII_XML_10,
                              const.VID_TAXII_XML_11,
                              const.VID_CERT_EU_JSON_10]:
        raise ValueError('Unsupported X-TAXII-Content-Type: {}'
                         .format(content_type))

    elif content_type == const.VID_CERT_EU_JSON_10:
        yield tm10.get_message_from_json(response.read())

    gen = etree.iterparse(response, events=('start', 'end'))

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

        yield _parse_full_tree(content_type, message_type, root)


def _parse_full_tree(content_type, message_type, elem):

    if log.isEnabledFor(logging.DEBUG):
        log.debug("Response:\n%s", etree.tostring(elem, pretty_print=True))

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
