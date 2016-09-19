
import libtaxii.messages_10 as tm10

from . import constants as const
from .abstract import AbstractClient
from .converters import (
    to_subscription_response_entity, to_content_block_entity,
    to_collection_entities
)
from .exceptions import NotSupportedError
from .utils import (
    pack_content_bindings, get_utc_now, pack_content_binding
)


class Client10(AbstractClient):
    '''Client implementation for TAXII Specification v1.0

    Use :py:meth:`cabby.create_client` to create client instances.
    '''

    taxii_binding = const.XML_10_BINDING
    services_version = const.TAXII_SERVICES_10

    def _discovery_request(self, uri):
        request = tm10.DiscoveryRequest(message_id=self._generate_id())
        response = self._execute_request(request, uri=uri)
        return response

    def __subscription_status_request(self, action, collection_name,
                                      subscription_id=None, uri=None):
        request_parameters = dict(
            message_id=self._generate_id(),
            action=action,
            feed_name=collection_name,
            subscription_id=subscription_id
        )

        request = tm10.ManageFeedSubscriptionRequest(**request_parameters)
        response = self._execute_request(
            request, uri=uri, service_type=const.SVC_FEED_MANAGEMENT)

        return to_subscription_response_entity(response, version=10)

    def get_subscription_status(self, collection_name, subscription_id=None,
                                uri=None):
        '''Get subscription status from TAXII Feed Management service.

        Sends a subscription request with action `STATUS`.
        If no ``subscription_id`` is provided, server will return
        the list of all available subscriptions for feed with a name
        specified in ``collection_name``.

        if ``uri`` is not provided, client will try to discover services and
        find Feed Management Service among them.

        :param str collection_name: target feed name
        :param str subscription_id: subscription ID (optional)
        :param str uri: URI path to a specific Collection Management service

        :return: subscription information response
        :rtype: :py:class:`cabby.entities.SubscriptionResponse`

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

        return self.__subscription_status_request(
            const.ACT_STATUS, collection_name, subscription_id=subscription_id,
            uri=uri)

    def unsubscribe(self, collection_name, subscription_id, uri=None):
        '''Unsubscribe from a subscription.

        Sends a subscription request with action `UNSUBSCRIBE`.
        Subscription is identified by ``collection_name`` and
        ``subscription_id``.

        if ``uri`` is not provided, client will try to discover services and
        find Collection Management Service among them.

        :param str collection_name: target feed name
        :param str subscription_id: subscription ID
        :param str uri: URI path to a specific TAXII service

        :return: subscription information response
        :rtype: :py:class:`cabby.entities.SubscriptionResponse`

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

        return self.__subscription_status_request(
            const.ACT_UNSUBSCRIBE, collection_name,
            subscription_id=subscription_id, uri=uri)

    def subscribe(self, collection_name, inbox_service=None,
                  content_bindings=None, uri=None, count_only=False):
        '''Create a subscription.

        Sends a subscription request with action `SUBSCRIBE`.

        if ``uri`` is not provided, client will try to discover services and
        find Collection Management Service among them.

        Content Binding subtypes are not supported in TAXII Specification v1.0.

        :param str collection_name: target feed name
        :param `cabby.entities.InboxService` inbox_service:
                Inbox Service that will accept content pushed by TAXII Server
                in the context of this subscription
        :param list content_bindings: a list of strings or
                :py:class:`cabby.entities.ContentBinding` entities
        :param str uri: URI path to a specific Collection Management service
        :param bool count_only: IGNORED. Count Only is not supported in
               TAXII 1.0 and added here only for method unification purpose.

        :return: subscription information response
        :rtype: :py:class:`cabby.entities.SubscriptionResponse`

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

        request_parameters = dict(
            message_id=self._generate_id(),
            action=const.ACT_SUBSCRIBE,
            feed_name=collection_name,
        )

        if inbox_service:
            binding = (inbox_service.message_bindings[0]
                       if inbox_service.message_bindings else '')
            delivery_parameters = tm10.DeliveryParameters(
                inbox_protocol=inbox_service.protocol,
                inbox_address=inbox_service.address,
                delivery_message_binding=binding
            )
            if content_bindings:
                delivery_parameters['content_bindings'] = [
                    tm10.ContentBinding(cb.binding_id)
                    for cb in content_bindings]

            request_parameters['delivery_parameters'] = delivery_parameters

        request = tm10.ManageFeedSubscriptionRequest(**request_parameters)
        response = self._execute_request(
            request, uri=uri, service_type=const.SVC_FEED_MANAGEMENT)

        return to_subscription_response_entity(response, version=10)

    def push(self, content, content_binding, uri=None, timestamp=None):
        '''Push content into Inbox Service.

        if ``uri`` is not provided, client will try to discover services and
        find Inbox Service among them.

        Content Binding subtypes and Destionation collections are not
        supported in TAXII Specification v1.0.

        :param str content: content to push
        :param content_binding: content binding for a content
        :type content_binding: string or
                               :py:class:`cabby.entities.ContentBinding`
        :param datetime timestamp: timestamp label of the content block
                (current UTC time by default)
        :param str uri: URI path to a specific Inbox Service

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

        content_block = tm10.ContentBlock(
            content=content,
            content_binding=pack_content_binding(content_binding, version=10),
            timestamp_label=timestamp or get_utc_now()
        )

        inbox_message = tm10.InboxMessage(message_id=self._generate_id(),
                                          content_blocks=[content_block])

        self._execute_request(inbox_message, uri=uri,
                              service_type=const.SVC_INBOX)
        self.log.debug("Content block successfully pushed")

    def get_collections(self, uri=None):
        '''Get collections from Feed Management Service.

        if ``uri`` is not provided, client will try to discover services and
        find Feed Management Service among them.

        :param str uri: URI path to a specific Feed Management service

        :return: list of collections
        :rtype: list of :py:class:`cabby.entities.Collection`

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

        request = tm10.FeedInformationRequest(message_id=self._generate_id())
        response = self._execute_request(
            request, uri=uri, service_type=const.SVC_FEED_MANAGEMENT)

        return to_collection_entities(response.feed_informations, version=10)

    def get_content_count(self, *args, **kwargs):
        '''Not supported in TAXII 1.0

        :raises `cabby.exceptions.NotSupportedError`:
                not supported in TAXII 1.0
        '''
        raise NotSupportedError(self.taxii_version)

    def poll(self, collection_name, begin_date=None, end_date=None,
             subscription_id=None, content_bindings=None, uri=None):
        '''Poll content from Polling Service.

        if ``uri`` is not provided, client will try to discover services and
        find Polling Service among them.

        :param str collection_name: feed to poll
        :param datetime begin_date:
               ask only for content blocks created after
               `begin_date` (exclusive)
        :param datetime end_date:
               ask only for content blocks created before
               `end_date` (inclusive)
        :param str subsctiption_id: ID of the existing subscription
        :param list content_bindings:
               list of stings or
               :py:class:`cabby.entities.ContentBinding` objects
        :param str uri: URI path to a specific Inbox Service

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

        _bindings = pack_content_bindings(content_bindings, version=10)
        data = dict(
            message_id=self._generate_id(),
            feed_name=collection_name,
            exclusive_begin_timestamp_label=begin_date,
            inclusive_end_timestamp_label=end_date,
            content_bindings=_bindings
        )

        if subscription_id:
            data['subscription_id'] = subscription_id

        request = tm10.PollRequest(**data)
        stream = self._execute_request(request, uri=uri,
                                       service_type=const.SVC_POLL)
        for obj in stream:
            if isinstance(obj, tm10.ContentBlock):
                yield to_content_block_entity(obj)

    def fulfilment(self, *args, **kwargs):
        '''Not supported in TAXII 1.0

        :raises `cabby.exceptions.NotSupportedError`:
        '''
        raise NotSupportedError(self.taxii_version)
