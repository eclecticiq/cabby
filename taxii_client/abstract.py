import urlparse

from libtaxii.clients import HttpClient
from libtaxii.common import generate_message_id
from libtaxii.constants import ST_SUCCESS, ST_NOT_FOUND
from libtaxii import get_message_from_http_response

from .utils import configure_taxii_client_auth
from .exceptions import *

import logging
log = logging.getLogger(__name__)



class AbstractClient(object):

    def __init__(self, host, discovery_path=None, port=None, use_https=False, auth=dict()):

        self.host = host
        self.port = port or (443 if use_https else 80)

        self.server_id = '%s:%d' % (self.host, self.port)

        self.client = configure_taxii_client_auth(HttpClient(), **auth)
        self.client.set_use_https(use_https)

        self.discovery_path = discovery_path
        self.services = None


    def _execute_request(self, request, uri=None, service_type=None):

        if not uri and not service_type:
            raise IllegalArgumentError('Either URI or service_type need to be provided')
        elif not uri:
            service = self._get_service(service_type)
            uri = service.service_address

        p = urlparse.urlparse(uri)
        host = p.hostname or self.host
        port = p.port or self.port
        path = p.path

        log.info("Sending %s request to %s%s%s", request.message_type, host, (":%d" % port if port else ""), path)


        if log.isEnabledFor(logging.DEBUG):
            log.debug("Request:\n%s", request.to_xml(pretty_print=True))


        request_body = request.to_xml(pretty_print=True)
        response_raw = self.client.call_taxii_service2(host, path, self.taxii_version, request_body, port=port)
        response = get_message_from_http_response(response_raw, in_response_to='0')


        if log.isEnabledFor(logging.DEBUG):
            log.debug("Response:\n%s", response.to_xml(pretty_print=True))


        if hasattr(response, 'status_type'): # version agnostic
            if response.status_type == ST_SUCCESS:
                return True
            else:
                raise UnsuccessfulStatusError(response)

        return response


    def _generate_id(self):
        return generate_message_id()


    def _get_service(self, service_type):

        candidates = self._get_all_services(service_type)

        if not candidates:
            raise ServiceNotFoundError("Service with type '%s' is not advertised" % service_type)
        elif len(candidates) > 1:
            raise AmbiguousServicesError("%d services found with type '%s'. Specify the exact URI" % (len(candidates), service_type))

        return candidates[0]


    def _get_all_services(self, service_type):
        if not self.services:
            try:
                self.discover_services()
            except ClientException, e:
                log.error('Can not automatically discover advertised services')
                raise e

        return filter(lambda i: i.service_type == service_type, self.services)


    def discover_services(self, uri=None):

        uri = uri or self.discovery_path

        if not uri:
            raise IllegalArgumentError('Discovery service path is not specified')

        response = self._discovery_request(uri)

        self.services = response.service_instances

        return self.services


