import logging
import urlparse

from libtaxii.clients import HttpClient
from libtaxii.common import generate_message_id
from libtaxii.constants import ST_SUCCESS, ST_NOT_FOUND
from libtaxii import get_message_from_http_response

from .utils import configure_taxii_client_auth
from .exceptions import (
        NoURIProvidedError, UnsuccessfulStatusError, ServiceNotFoundError,
        AmbiguousServicesError, ClientException
)


class AbstractClient(object):

    def __init__(self, host, discovery_path=None, port=None, use_https=False, auth=None):

        self.host = host
        self.port = port or (443 if use_https else 80)
        self.use_https = use_https
        self.auth = auth

        self.discovery_path = discovery_path
        self.services = None

        self.log = logging.getLogger("%s.%s" % (self.__module__, self.__class__.__name__))


    @staticmethod
    def _create_client(auth={}, use_https=False):
        client = configure_taxii_client_auth(HttpClient(), **(auth or {}))
        client.set_use_https(use_https)
        return client


    def _execute_request(self, request, uri=None, service_type=None):

        if not uri and not service_type:
            raise NoURIProvidedError('Either URI or service_type need to be provided')
        elif not uri:
            service = self._get_service(service_type)
            uri = service.service_address

        parsed = urlparse.urlparse(uri)
        if not parsed.scheme:
            parsed = urlparse.urlparse("http://" + uri) # faking schema because otherwise urlparse gets confused

        host = parsed.hostname or self.host
        port = parsed.port or self.port
        path = parsed.path

        auth = self.auth
        use_https = self.use_https or (parsed.scheme == 'https')

        full_path = "%(host)s:%(port)s%(path)s" % dict(host=host, port=port, path=path)

        client = AbstractClient._create_client(auth=auth, use_https=use_https)

        request_body = request.to_xml(pretty_print=True)

        self.log.info("Sending %s to %s", request.message_type, full_path)
        self.log.debug("Request:\n%s", request_body)

        response_raw = client.call_taxii_service2(host, path, self.taxii_version, request_body, port=port)

        response = get_message_from_http_response(response_raw, in_response_to='0')

        self.log.info("Response received for %s from %s", request.message_type, full_path)
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug("Response:\n%s", response.to_xml(pretty_print=True))

        if hasattr(response, 'status_type'): # version agnostic
            if response.status_type != ST_SUCCESS:
                raise UnsuccessfulStatusError(response)
            return True

        return response


    def _generate_id(self):
        return generate_message_id()


    def _get_service(self, service_type):

        candidates = self.get_services(service_type=service_type)

        if not candidates:
            raise ServiceNotFoundError("Service with type '%s' is not advertised" % service_type)
        elif len(candidates) > 1:
            raise AmbiguousServicesError("%d services found with type '%s'. Specify the exact URI" % (len(candidates), service_type))

        return candidates[0]


    def get_services(self, service_type=[], service_types=[]):
        if not self.services:
            try:
                services = self.discover_services()
            except ClientException, e:
                self.log.error('Can not automatically discover advertised services')
                raise e
        else:
            services = self.services

        if not service_type and not service_types:
            return services

        if service_type:
            filter_func = lambda i: i.service_type == service_type

        if service_types:
            filter_func = lambda i: i.service_type in service_types

        return filter(filter_func, services)


    def discover_services(self, uri=None, cache=True):

        uri = uri or self.discovery_path

        if not uri:
            raise NoURIProvidedError('Discovery service URI is not specified')

        response = self._discovery_request(uri)
        services = response.service_instances

        type_to_count = {}
        for s in services:
            type_to_count[s.service_type] = type_to_count.get(s.service_type, 0) + 1

        self.log.info("%d services discovered: %s", len(services), ", ".join(["%s=%s" % x for x in type_to_count.items()]))

        if cache:
            self.services = services

        return services

