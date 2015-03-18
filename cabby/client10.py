from itertools import imap

import libtaxii.messages_10 as tm10
from libtaxii import constants as const

from .abstract import AbstractClient
from .converters import (
    to_subscription_response_entity, to_content_block_entity,
    to_collection_entities
)
from .utils import pack_content_bindings


class Client10(AbstractClient):

    taxii_version = const.VID_TAXII_XML_10
    services_version = const.VID_TAXII_SERVICES_10

    def _discovery_request(self, uri):
        request = tm10.DiscoveryRequest(message_id=self._generate_id())
        response = self._execute_request(request, uri=uri)
        return response


    def __subscription_status_request(self, action, feed_name,
            subscription_id=None, uri=None):

        request_parameters = dict(
            message_id = self._generate_id(),
            action = action,
            feed_name = feed_name,
            subscription_id = subscription_id
        )

        request = tm10.ManageFeedSubscriptionRequest(**request_parameters)
        response = self._execute_request(request, uri=uri,
                service_type=const.SVC_FEED_MANAGEMENT)

        return to_subscription_response_entity(response, version=10)


    def get_subscription_status(self, feed_name, subscription_id=None,
            uri=None):

        return self.__subscription_status_request(const.ACT_STATUS,
                feed_name, subscription_id=subscription_id, uri=uri)


    def unsubscribe(self, feed_name, subscription_id=None, uri=None):

        return self.__subscription_status_request(const.ACT_UNSUBSCRIBE,
                feed_name, subscription_id=subscription_id, uri=uri)


    def push(self, content, content_binding, uri=None):

        #Subtype is not supported in TAXII version 1.0
        #Destination collections are not supported in TAXII version 1.0

        content_block = tm10.ContentBlock(content_binding, content)
        inbox_message = tm10.InboxMessage(message_id=self._generate_id(),
                content_blocks=[content_block])

        self._execute_request(inbox_message, uri=uri,
                service_type=const.SVC_INBOX)

        self.log.debug("Content successfully pushed")


    def subscribe(self, feed_name, inbox_service=None,
            content_bindings=None, uri=None):

        request_parameters = dict(
            message_id = self._generate_id(),
            action = const.ACT_SUBSCRIBE,
            feed_name = feed_name,
        )

        if inbox_service:
            delivery_parameters = tm10.DeliveryParameters(
                inbox_protocol = inbox_service.protocol,
                inbox_address = inbox_service.address,
                delivery_message_binding = inbox_service.message_bindings[0] \
                        if inbox_service.message_bindings else ''
            )
            if content_bindings:
                delivery_parameters['content_bindings'] = [tm10.ContentBinding(cb.binding_id) \
                        for cb in content_bindings]

            request_parameters['delivery_parameters'] = delivery_parameters

        request = tm10.ManageFeedSubscriptionRequest(**request_parameters)
        response = self._execute_request(request, uri=uri, service_type=const.SVC_FEED_MANAGEMENT)

        return to_subscription_response_entity(response, version=10)


    def get_collections(self, uri=None):

        request = tm10.FeedInformationRequest(message_id=self._generate_id())
        response = self._execute_request(request, uri=uri, service_type=const.SVC_FEED_MANAGEMENT)

        return to_collection_entities(response.feed_informations, version=10)


    def poll(self, feed_name, begin_date=None, end_date=None,
            subscription_id=None, content_bindings=None, uri=None):

        data = dict(
            message_id = self._generate_id(),
            feed_name = feed_name,
            exclusive_begin_timestamp_label = begin_date,
            inclusive_end_timestamp_label = end_date,
            content_bindings = pack_content_bindings(content_bindings, version=10)
        )

        if subscription_id:
            data['subscription_id'] = subscription_id

        request = tm10.PollRequest(**data)
        response = self._execute_request(request, uri=uri, service_type=const.SVC_POLL)

        return imap(to_content_block_entity, response.content_blocks)


    # No poll fulfillment in TAXII 1.0
