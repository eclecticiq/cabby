import urlparse

from libtaxii.clients import HttpClient
from libtaxii.common import generate_message_id
from libtaxii.constants import ST_SUCCESS
from libtaxii import get_message_from_http_response

from .utils import configure_taxii_client_auth

import logging
log = logging.getLogger(__name__)

class StatusMessage(object):

    def __init__(self, status, text=None):
        self.status = status
        self.text = text

    @staticmethod
    def from_status(taxii_status):
        return StatusMessage(taxii_status.status_type, text=taxii_status.to_text())


class AbstractClient(object):

    def __init__(self, host, port=None, use_https=False, auth=dict()):

        self.host = host
        self.port = port or (443 if use_https else 80)

        self.server_id = '%s:%d' % (self.host, self.port)

        self.client = configure_taxii_client_auth(HttpClient(), **auth)
        self.client.set_use_https(use_https)

        self.services = None


    def _execute_request(self, request, uri=None, service_type=None):

        if not uri and not service_type:
            raise ValueError('Either URI or service_type needs to be provided')
        elif not uri:
            service = self._get_service(service_type)
            uri = service.service_address

        p = urlparse.urlparse(uri)
        host = p.hostname or self.host
        port = p.port or self.port
        path = p.path

        log.info("Sending request to %s%s%s", host, (":%d" % port if port else ""), path)


        if log.isEnabledFor(logging.DEBUG):
            log.debug("Request:\n%s", request.to_xml(pretty_print=True))


        request_body = request.to_xml(pretty_print=True)
        response_raw = self.client.call_taxii_service2(host, path, self.taxii_version, request_body, port=port)
        response = get_message_from_http_response(response_raw, in_response_to='0')


        if log.isEnabledFor(logging.DEBUG):
            log.debug("Response:\n%s", response.to_xml(pretty_print=True))

        if hasattr(response, 'status_type'):
            return StatusMessage.from_status(response)

        return response


    def _generate_id(self):
        return generate_message_id()


    def _get_service(self, service_type):
        if not self.services:
            self.discover_services(uri=None)

        candidates = filter(lambda i: i.service_type == service_type, self.services)

        if not candidates:
            raise Exception("Service with type '%s' is not advertised" % service_type)
        elif len(candidates) > 1:
            raise Exception("%d services found with type '%s', unclear which one to use. Specify the exact URI" % (len(candidates), service_type))

        return candidates[0]

