import logging
import urlparse
import urllib2

from libtaxii.clients import HttpClient
from libtaxii.common import generate_message_id
from libtaxii import constants as const
from libtaxii import get_message_from_http_response

from .converters import to_detailed_service_instance_entity
from .utils import configure_client_auth
from .exceptions import (
    NoURIProvidedError, UnsuccessfulStatusError, ServiceNotFoundError,
    AmbiguousServicesError, ClientException, HTTPError
)


class AbstractClient(object):
    '''Abstract client class.

    This class can not be used directly, use :py:meth:`cabby.create_client`
    to create client instances.
    '''

    NO_PROXY = HttpClient.NO_PROXY
    PROXY_TYPE_CHOICES = [HttpClient.PROXY_HTTP, HttpClient.PROXY_HTTPS]
    SUPPORTED_SCHEMES = ['http', 'https']

    def __init__(self, host=None, discovery_path=None, port=None,
            use_https=False, headers=None):

        self.host = host
        self.port = port or (443 if use_https else 80)
        self.use_https = use_https

        self.discovery_path = discovery_path
        self.services = None

        self.auth = None
        self.proxy_details = None

        self.headers = headers

        self.log = logging.getLogger("%s.%s" % (self.__module__,
            self.__class__.__name__))

    def set_auth(self, cert_file=None, key_file=None, username=None,
            password=None):
        '''Set authentication credentials.

        Authentication types can be combined. It is possible to use
        only SSL authentication, only basic authentication, or 
        basic authentication over SSL.

        :param str cert_file: a path to SSL certificate file
        :param str key_file: a path to SSL key file
        :param str username: basic authentication username
        :param str password: basic authentication password
        '''

        self.auth = {
            'cert_file' : cert_file,
            'key_file' : key_file,
            'username' : username,
            'password' : password
        }

    def set_proxy(self, proxy_url, proxy_type=None):
        '''Set proxy properties.

        :param str proxy_url: proxy address formated as an URL or
                              :attr:`NO_PROXY` to force client not
                              to use proxy.
        :param str proxy_type: one of the values
                              from :attr:`PROXY_TYPE_CHOICES`
        '''

        if not proxy_url:
            return ValueError('proxy_url can not be None')

        if (proxy_url != NO_PROXY and not proxy_type) or \
                (proxy_type and proxy_type not in PROXY_TYPE_CHOICES):
            types = ", ".join(PROXY_TYPE_CHOICES)
            return ValueError('proxy_type needs to to be one of: %s' % types)

        self.proxy_details = {
            'proxy_type' : proxy_type,
            'proxy_string' : proxy_url
        }

    @staticmethod
    def _create_client(auth=None, use_https=False, proxy_details=None):

        client = HttpClient(use_https=use_https)
        client = configure_client_auth(client, **(auth or {}))

        if proxy_details:
            client.set_proxy(**proxy_details)

        return client

    def _execute_request(self, request, uri=None, service_type=None):
        '''Execute generic TAXII request.

        A service is defined by ``uri`` parameter or is chosen from pre-cached
        services by ``service_type``.
        '''
        
        if not uri and not service_type:
            raise NoURIProvidedError('URI or service_type needs to be provided')
        elif not uri:
            service = self._get_service(service_type)
            uri = service.address

        parsed = urlparse.urlparse(uri)
        if not parsed.scheme:
            # faking schema because otherwise urlparse gets confused
            parsed = urlparse.urlparse("http://" + uri)
        elif parsed.scheme not in self.SUPPORTED_SCHEMES:
            raise ValueError('Scheme "%s" is not supported. Use one of: %s' % \
                    (parsed.scheme, ', '.join(self.SUPPORTED_SCHEMES)))

        use_https = self.use_https or (parsed.scheme == 'https')

        host = parsed.hostname or self.host
        port = parsed.port or (443 if use_https else self.port)
        path = parsed.path

        full_path = "http%(https)s://%(host)s:%(port)s%(path)s" % dict(
                https=('s' if use_https else ''), host=host, port=port,
                path=path)

        if not host:
            raise ValueError('Host name is not provided: %s' % full_path)

        client = AbstractClient._create_client(
                auth=self.auth, use_https=use_https)

        request_body = request.to_xml(pretty_print=True)

        full_path = "http%(https)s://%(host)s:%(port)s%(path)s" % dict(
                https=('s' if use_https else ''), host=host, port=port,
                path=path)
        self.log.info("Sending %s to %s", request.message_type, full_path)
        self.log.debug("Request:\n%s", request_body)

        response_raw = client.call_taxii_service2(
            host, path, self.taxii_version, request_body, port=port,
            headers=self.headers)

        # https://github.com/TAXIIProject/libtaxii/issues/181
        if isinstance(response_raw, urllib2.URLError):
            error = response_raw
            self.log.debug("%s: %s", error, error.read())
            raise HTTPError(error)

        response = get_message_from_http_response(
            response_raw, in_response_to='0')

        self.log.info("Response received for %s from %s",
                request.message_type, full_path)

        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug("Response:\n%s", response.to_xml(pretty_print=True))

        if hasattr(response, 'status_type'):
            if response.status_type != const.ST_SUCCESS:
                raise UnsuccessfulStatusError(response)
        else:
            return response

    def _generate_id(self):
        return generate_message_id(version=self.services_version)

    def _get_service(self, service_type):

        candidates = self.get_services(service_type=service_type)

        if not candidates:
            raise ServiceNotFoundError(
                "Service with type '%s' is not advertised" % service_type)
        elif len(candidates) > 1:
            raise AmbiguousServicesError(
                "%d services found with type '%s'. Specify the exact URI" % (
                    len(candidates), service_type))

        return candidates[0]

    def get_services(self, service_type=None, service_types=None):
        '''Get services advertised by TAXII server.

        This method will try to do automatic discovery by calling
        :py:meth:`discover_services`.

        :param str service_type: filter services by specific type. Accepted
                                 values are listed in
                                 :py:data:`cabby.entities.SERVICE_TYPES`
        :param str service_types: filter services by multiple types. Accepted
                                 values are listed in
                                 :py:data:`cabby.entities.SERVICE_TYPES`

        :return: list of service instances
        :rtype: list of :py:class:`cabby.entities.DetailedServiceInstance`
                (or :py:class:`cabby.entities.InboxDetailedService`)
        
        :raises ValueError:
                if URI provided is invalid or schema is not supported
        :raises `cabby.exceptions.HTTPError`:
                if HTTP error happened
        :raises `cabby.exceptions.UnsuccessfulStatusError`:
                if Status Message received and status_type is not `SUCCESS`
        :raises `cabby.exceptions.ServiceNotFoundError`:
                if no service found
        :raises `cabby.exceptions.AmbiguousServicesError`:
                more than one service with type specified
        :raises `cabby.exceptions.NoURIProvidedError`:
                no URI provided and client can't discover services
        '''
        if not self.services:
            try:
                services = self.discover_services()
            except ClientException, e:
                self.log.error('Can not autodiscover advertised services')
                raise e
        else:
            services = self.services

        if not service_type and not service_types:
            return services

        if service_type:
            filter_func = lambda s: s.type == service_type
        elif service_types:
            filter_func = lambda s: s.type in service_types

        return filter(filter_func, services)

    def discover_services(self, uri=None, cache=True):
        '''Discover services advertised by TAXII server.

        This method will send discovery request to a service, defined by ``uri``
        or constructor's connection parameters.

        :param str uri: URI path to a specific TAXII service
        :param bool cache: if discovered services should be cached

        :return: list of TAXII services
        :rtype: list of :py:class:`cabby.entities.DetailedServiceInstance`
                (or :py:class:`cabby.entities.InboxDetailedService`)

        :raises ValueError:
                if URI provided is invalid or schema is not supported
        :raises `cabby.exceptions.HTTPError`:
                if HTTP error happened
        :raises `cabby.exceptions.UnsuccessfulStatusError`:
                if Status Message received and status_type is not `SUCCESS`
        :raises `cabby.exceptions.ServiceNotFoundError`:
                if no service found
        :raises `cabby.exceptions.AmbiguousServicesError`:
                more than one service with type specified
        :raises `cabby.exceptions.NoURIProvidedError`:
                no URI provided and client can't discover services
        '''

        uri = uri or self.discovery_path

        if not uri:
            raise NoURIProvidedError('Discovery service URI is not specified')

        response = self._discovery_request(uri)

        services = map(to_detailed_service_instance_entity,
                response.service_instances)

        self.log.info("%d services discovered", len(services))

        if cache:
            self.services = services

        return services

