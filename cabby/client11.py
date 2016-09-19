
import libtaxii.messages_11 as tm11

from . import constants as const
from .abstract import AbstractClient
from .entities import ContentBlockCount
from .converters import (
    to_subscription_response_entity, to_content_block_entity,
    to_collection_entities
)
from .utils import (
    pack_content_bindings, get_utc_now, pack_content_binding
)


class Client11(AbstractClient):
    '''Client implementation for TAXII Specification v1.1

    Use :py:meth:`cabby.create_client` to create client instances.
    '''

    taxii_binding = const.XML_11_BINDING
    services_version = const.TAXII_SERVICES_11

    def _discovery_request(self, uri):
        request = tm11.DiscoveryRequest(message_id=self._generate_id())
        response = self._execute_request(request, uri=uri)
        return response

    def __subscription_status_request(self, action, collection_name,
                                      subscription_id=None, uri=None):

        request_params = dict(
            message_id=self._generate_id(),
            action=action,
            collection_name=collection_name,
            subscription_id=subscription_id
        )

        request = tm11.ManageCollectionSubscriptionRequest(**request_params)
        response = self._execute_request(
            request, uri=uri,
            service_type=const.SVC_COLLECTION_MANAGEMENT)

        return to_subscription_response_entity(response, version=11)

    def get_subscription_status(self, collection_name,
                                subscription_id=None, uri=None):
        '''Get subscription status from TAXII Collection Management service.

        Sends a subscription request with action `STATUS`.
        If no ``subscription_id`` is provided, server will return the list
        of all available subscriptions for a collection with a name
        specified in ``collection_name``.

        if ``uri`` is not provided, client will try to discover services and
        find Collection Management Service among them.

        :param str collection_name: target collection name
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
                if no Collection Management service found
        :raises `cabby.exceptions.AmbiguousServicesError`:
                more than one service with type specified
        :raises `cabby.exceptions.NoURIProvidedError`:
                no URI provided and client can't discover services
        '''

        return self.__subscription_status_request(
            const.ACT_STATUS, collection_name, subscription_id=subscription_id,
            uri=uri)

    def pause_subscription(self, collection_name, subscription_id, uri=None):
        '''Pause a subscription.

        Sends a subscription request with action `PAUSE`.  Subscription is
        identified by ``collection_name`` and ``subscription_id``.

        if ``uri`` is not provided, client will try to discover services and
        find Collection Management Service among them.

        :param str collection_name: target collection name
        :param str subscription_id: subscription ID
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
            const.ACT_PAUSE, collection_name, subscription_id=subscription_id,
            uri=uri)

    def resume_subscription(self, collection_name, subscription_id, uri=None):
        '''Resume a subscription.

        Sends a subscription request with action `RESUME`.
        Subscription is identified by ``collection_name``
        and ``subscription_id``.

        if ``uri`` is not provided, client will try to discover services and
        find Collection Management Service among them.

        :param str collection_name: target collection name
        :param str subscription_id: subscription ID
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
            const.ACT_RESUME, collection_name,
            subscription_id=subscription_id, uri=uri)

    def unsubscribe(self, collection_name, subscription_id, uri=None):
        '''Unsubscribe from a subscription.

        Sends a subscription request with action `UNSUBSCRIBE`. Subscription
        is identified by ``collection_name`` and ``subscription_id``.

        if ``uri`` is not provided, client will try to discover services and
        find Collection Management Service among them.

        :param str collection_name: target collection name
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

    def subscribe(self, collection_name, count_only=False, inbox_service=None,
                  content_bindings=None, uri=None):
        '''Create a subscription.

        Sends a subscription request with action `SUBSCRIBE`.

        if ``uri`` is not provided, client will try to discover services and
        find Collection Management Service among them.

        :param str collection_name: target collection name
        :param bool count_only: subscribe only to counts and not full content
        :param `cabby.entities.InboxService` inbox_service:
                Inbox Service that will accept content pushed by TAXII Server
                in the context of this subscription
        :param list content_bindings: a list of strings or
                :py:class:`cabby.entities.ContentBinding` entities
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

        response_type = const.RT_COUNT_ONLY if count_only else const.RT_FULL

        sparams = tm11.SubscriptionParameters(
            response_type=response_type,
            content_bindings=pack_content_bindings(content_bindings,
                                                   version=11)
        )
        rparams = dict(
            message_id=self._generate_id(),
            action=const.ACT_SUBSCRIBE,
            collection_name=collection_name,
            subscription_parameters=sparams,
        )

        if inbox_service:
            binding = (inbox_service.message_bindings[0]
                       if inbox_service.message_bindings else '')

            rparams['push_parameters'] = tm11.PushParameters(
                inbox_protocol=inbox_service.protocol,
                inbox_address=inbox_service.address,
                delivery_message_binding=binding
            )

        request = tm11.ManageCollectionSubscriptionRequest(**rparams)
        response = self._execute_request(
            request, uri=uri,
            service_type=const.SVC_COLLECTION_MANAGEMENT)

        return to_subscription_response_entity(response, version=11)

    def get_collections(self, uri=None):
        '''Get collections from Collection Management Service.

        if ``uri`` is not provided, client will try to discover services and
        find Collection Management Service among them.

        :param str uri: URI path to a specific Collection Management service

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

        request = tm11.CollectionInformationRequest(
            message_id=self._generate_id())

        response = self._execute_request(
            request, uri=uri,
            service_type=const.SVC_COLLECTION_MANAGEMENT)

        return to_collection_entities(response.collection_informations,
                                      version=11)

    def push(self, content, content_binding, collection_names=None,
             timestamp=None, uri=None):
        '''Push content into Inbox Service.

        if ``uri`` is not provided, client will try to discover
        services and find Inbox Service among them.

        :param str content: content to push
        :param content_binding: content binding for a content
        :type content_binding: string or
                               :py:class:`cabby.entities.ContentBinding`
        :param list collection_names:
                destination collection names
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

        content_block = tm11.ContentBlock(
            content=content,
            content_binding=pack_content_binding(content_binding, version=11),
            timestamp_label=timestamp or get_utc_now()
        )

        inbox_message = tm11.InboxMessage(message_id=self._generate_id(),
                                          content_blocks=[content_block])

        if collection_names:
            inbox_message.destination_collection_names.extend(collection_names)

        self._execute_request(inbox_message, uri=uri,
                              service_type=const.SVC_INBOX)

        self.log.debug("Content block successfully pushed")

    def _prepare_poll_request(self, collection_name, begin_date=None,
                              end_date=None, subscription_id=None,
                              inbox_service=None, content_bindings=None,
                              count_only=False):
        data = dict(
            message_id=self._generate_id(),
            collection_name=collection_name,
            exclusive_begin_timestamp_label=begin_date,
            inclusive_end_timestamp_label=end_date
        )

        if subscription_id:
            data['subscription_id'] = subscription_id
        else:
            _bindings = pack_content_bindings(content_bindings, version=11)
            poll_params = {'content_bindings': _bindings}

            if inbox_service:
                message_bindings = inbox_service.message_bindings[0] \
                    if inbox_service.message_bindings else []

                poll_params['delivery_parameters'] = tm11.DeliveryParameters(
                    inbox_protocol=inbox_service.protocol,
                    inbox_address=inbox_service.address,
                    delivery_message_binding=message_bindings
                )
                poll_params['allow_asynch'] = True

            if count_only:
                poll_params['response_type'] = const.RT_COUNT_ONLY
            else:
                poll_params['response_type'] = const.RT_FULL

            data['poll_parameters'] = \
                tm11.PollRequest.PollParameters(**poll_params)

        return tm11.PollRequest(**data)

    def get_content_count(self, collection_name, begin_date=None,
                          end_date=None, subscription_id=None,
                          inbox_service=None, content_bindings=None, uri=None):
        '''Get content blocks count for a query.

        if ``uri`` is not provided, client will try to discover services and
        find Polling Service among them.

        If ``subscription_id`` provided, arguments ``content_bindings`` and
        ``inbox_service`` are ignored.

        :param str collection_name: collection to poll
        :param datetime begin_date: ask only for content blocks created
               after `begin_date` (exclusive)
        :param datetime end_date: ask only for content blocks created
               before `end_date` (inclusive)
        :param str subsctiption_id: ID of the existing subscription
        :param `cabby.entities.InboxService` inbox_service:
               Inbox Service that will accept content pushed by TAXII Server
               in the context of this Poll Request
        :param list content_bindings: list of stings or
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

        :rtype: :py:class:`cabby.entities.ContentBlockCount`
        '''

        request = self._prepare_poll_request(
            collection_name,
            begin_date=begin_date,
            end_date=end_date,
            subscription_id=subscription_id,
            inbox_service=inbox_service,
            content_bindings=content_bindings,
            count_only=True
        )
        response = self._execute_request(
            request, uri=uri, service_type=const.SVC_POLL)

        for obj in response:
            if isinstance(obj, tm11.PollResponse):
                if obj.record_count:
                    return ContentBlockCount(
                        count=obj.record_count.record_count,
                        is_partial=obj.record_count.partial_count
                    )
                else:
                    return None

    def poll(self, collection_name, begin_date=None, end_date=None,
             subscription_id=None, inbox_service=None,
             content_bindings=None, uri=None):
        '''Poll content from Polling Service.

        if ``uri`` is not provided, client will try to discover services and
        find Polling Service among them.

        If ``subscription_id`` provided, arguments ``content_bindings`` and
        ``inbox_service`` are ignored.

        :param str collection_name: collection to poll
        :param datetime begin_date: ask only for content blocks created
               after `begin_date` (exclusive)
        :param datetime end_date: ask only for content blocks created
               before `end_date` (inclusive)
        :param str subsctiption_id: ID of the existing subscription
        :param `cabby.entities.InboxService` inbox_service:
               Inbox Service that will accept content pushed by TAXII Server
               in the context of this Poll Request
        :param list content_bindings: list of stings or
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

        request = self._prepare_poll_request(
            collection_name,
            begin_date=begin_date,
            end_date=end_date,
            subscription_id=subscription_id,
            inbox_service=inbox_service,
            content_bindings=content_bindings,
            count_only=False
        )

        stream = self._execute_request(request, uri=uri,
                                       service_type=const.SVC_POLL)
        response = None
        for obj in stream:
            if isinstance(obj, tm11.ContentBlock):
                yield to_content_block_entity(obj)
            else:
                response = obj
                break

        if response and response.more:
            part = response.result_part_number

            while True:
                part += 1
                has_data = False

                fulfilment_stream = self.fulfilment(
                    collection_name, response.result_id,
                    part_number=part, uri=uri)

                for block in fulfilment_stream:
                    has_data = True
                    yield block

                if not has_data:
                    break

    def fulfilment(self, collection_name, result_id, part_number=1, uri=None):
        '''Poll content from Polling Service as a part of fulfilment process.

        if ``uri`` is not provided, client will try to discover services and
        find Polling Service among them.

        :param str collection_name: collection to poll
        :param str result_id: existing polling Result ID
        :param int part_number: index number of a part from the result set
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

        request = tm11.PollFulfillmentRequest(
            message_id=self._generate_id(),
            collection_name=collection_name,
            result_id=result_id,
            result_part_number=part_number
        )

        stream = self._execute_request(request, uri=uri,
                                       service_type=const.SVC_POLL)

        for obj in stream:
            if isinstance(obj, tm11.ContentBlock):
                yield to_content_block_entity(obj)
