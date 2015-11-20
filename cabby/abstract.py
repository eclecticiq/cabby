from furl import furl
import logging

from libtaxii.common import generate_message_id

from .converters import to_detailed_service_instance_entity
from .exceptions import (
    NoURIProvidedError, ServiceNotFoundError,
    AmbiguousServicesError, ClientException
)
from .dispatcher import send_taxii_request
from six.moves import map


class AbstractClient(object):
    '''Abstract client class.

    This class can not be used directly, use :py:meth:`cabby.create_client`
    to create client instances.
    '''

    SUPPORTED_SCHEMES = ['http', 'https']

    def __init__(self, host=None, discovery_path=None, port=None,
                 use_https=False, headers=None):

        self.host = host
        self.port = port or (443 if use_https else 80)
        self.use_https = use_https

        self.discovery_path = discovery_path
        self.services = None

        self.proxies = None
        self.auth_details = {}
        self.tls_auth = None
        self.verify_ssl = False

        self.headers = headers or {}

        self.log = logging.getLogger("%s.%s" % (self.__module__,
                                                self.__class__.__name__))

    def set_auth(self, cert_file=None, key_file=None, key_password=None,
                 username=None, password=None, jwt_auth_url=None,
                 verify_ssl=True):
        '''Set authentication credentials.

        ``jwt_auth_url`` is required for JWT based authentication. If
        it is not specified but ``username`` and ``password`` are provided,
        client will configure Basic authentication.

        SSL authentication can be combined with JWT and Basic
        authentication.

        :param str cert_file: a path to SSL certificate file
        :param str key_file: a path to SSL key file
        :param str username: username, used in basic auth or JWT auth
        :param str password: password, used in basic auth or JWT auth
        :param str key_password: same argument as in
            ``ssl.SSLContext.load_cert_chain`` - may be a function to call
            to get the password for decrypting the private key or
            string/bytes/bytearray. It will only be called if the private
            key is encrypted and a password is necessary.
        :param str jwt_auth_url: URL used to obtain JWT token
        :param bool/str verify_ssl: set to False to skip checking host's SSL
            certificate. Set to True to check certificate against public CAs or
            set to filepath to check against custom CA bundle.
        '''

        if cert_file and key_file:
            if key_password:
                self.tls_auth = (cert_file, key_file, key_password)
            else:
                self.tls_auth = (cert_file, key_file)
        else:
            self.tls_auth = None

        self.verify_ssl = verify_ssl

        self.auth_details = {
            'username': username,
            'password': password,
            'jwt_url': jwt_auth_url
        }

    def set_proxies(self, proxies):
        '''Set proxy properties.

        Cause requests to go through a proxy.
        Must be a dictionary mapping protocol names to URLs of proxies.

        :param dir proxies: dictionary mapping protocol names to URLs
        '''

        self.proxies = proxies

    def _prepare_url(self, uri):

        fu = furl(uri)

        if fu.scheme and fu.scheme not in self.SUPPORTED_SCHEMES:
            raise ValueError(
                'Scheme "{}" is not supported. Use one of: {}'
                .format(fu.scheme, ', '.join(self.SUPPORTED_SCHEMES)))

        use_https = self.use_https or (fu.scheme == 'https')

        fu.scheme = fu.scheme or ('https' if use_https else 'http')
        fu.host = fu.host or self.host
        fu.port = fu.port or (443 if use_https else self.port)

        if not fu.host:
            raise ValueError('Host name is not provided: {}'.format(fu.url))

        return fu.url

    def _execute_request(self, request, uri=None, service_type=None):
        '''Execute generic TAXII request.

        A service is defined by ``uri`` parameter or is chosen from pre-cached
        services by ``service_type``.
        '''

        if not uri and not service_type:
            raise NoURIProvidedError('URI or service_type needed')
        elif not uri:
            service = self._get_service(service_type)
            uri = service.address

        if self.auth_details.get('jwt_url'):
            self.auth_details['jwt_url'] = self._prepare_url(
                self.auth_details['jwt_url'])

        url = self._prepare_url(uri)
        message = send_taxii_request(url, request,
                                     headers=self.headers,
                                     proxies=self.proxies,
                                     tls_auth=self.tls_auth,
                                     verify_ssl=self.verify_ssl,
                                     **self.auth_details)

        return message

    def _generate_id(self):
        return generate_message_id(version=self.services_version)

    def _get_service(self, service_type):
        candidates = self.get_services(service_type=service_type)

        if not candidates:
            raise ServiceNotFoundError(
                "Service with type '{}' is not advertised"
                .format(service_type))

        elif len(candidates) > 1:
            raise AmbiguousServicesError(
                "{} services found with type '{}'. Specify the exact URI"
                .format(len(candidates), service_type))

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
        if self.services:
            services = self.services
        else:
            try:
                services = self.discover_services()
            except ClientException as e:
                self.log.error('Can not autodiscover advertised services')
                raise e

        if service_type:
            return [s for s in services if s.type == service_type]
        elif service_types:
            return [s for s in services if s.type in service_types]
        else:
            return services

    def discover_services(self, uri=None, cache=True):
        '''Discover services advertised by TAXII server.

        This method will send discovery request to a service, defined
        by ``uri`` or constructor's connection parameters.

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
                if no Discovery servicefound
        :raises `cabby.exceptions.AmbiguousServicesError`:
                more than one service with type specified
        :raises `cabby.exceptions.NoURIProvidedError`:
                no URI provided and client can't discover services
        '''

        uri = uri or self.discovery_path

        if not uri:
            raise NoURIProvidedError('Discovery service URI is not specified')

        response = self._discovery_request(uri)

        services = list(map(
            to_detailed_service_instance_entity,
            response.service_instances))

        self.log.info("%d services discovered", len(services))

        if cache:
            self.services = services

        return services
