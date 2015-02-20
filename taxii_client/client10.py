
import libtaxii.messages_10 as tm10
from libtaxii.constants import *

from .abstract import AbstractClient
from .utils import extract_content


class Client10(AbstractClient):

    taxii_version = VID_TAXII_XML_10


    def _discovery_request(self, uri):
        request = tm10.DiscoveryRequest(message_id=self._generate_id())
        response = self._execute_request(request, uri=uri)
        return response


    def __subscription_status_request(self, action, feed, subscription_id=None, uri=None):
        request_parameters = dict(
            message_id = self._generate_id(),
            action = action,
            feed_name = feed,
            subscription_id = subscription_id
        )

        request = tm10.ManageFeedSubscriptionRequest(**request_parameters)
        response = self._execute_request(request, uri=uri, service_type=SVC_FEED_MANAGEMENT)

        return response


    def get_subscription_status(self, feed, subscription_id=None, uri=None):

        return self.__subscription_status_request(ACT_STATUS, feed,
                subscription_id=subscription_id, uri=uri)


    def unsubscribe(self, feed, subscription_id=None, uri=None):

        return self.__subscription_status_request(ACT_UNSUBSCRIBE, feed,
                subscription_id=subscription_id, uri=uri)


    def push(self, content, content_binding, uri=None):

        #Subtype is not supported in TAXII version 1.0
        #Destination collections are not supported in TAXII version 1.0

        content_block = tm10.ContentBlock(content_binding, content)
        inbox_message = tm10.InboxMessage(message_id=self._generate_id(), content_blocks=[content_block])

        response = self._execute_request(inbox_message, uri=uri, service_type=SVC_INBOX)

        self.log.info("Content successfully pushed")


    def subscribe(self, feed, count_only=False, inbox_service=None, content_bindings=None, uri=None):

        request_parameters = dict(
            message_id = self._generate_id(),
            action = ACT_SUBSCRIBE,
            feed_name = feed,
        )

        if inbox_service:
            delivery_parameters = tm10.DeliveryParameters(
                inbox_protocol = inbox_service.protocol_binding,
                inbox_address = inbox_service.service_address,
                delivery_message_binding = inbox_service.message_bindings[0] if inbox_service.message_bindings else ''
            )
            if content_bindings:
                delivery_parameters['content_bindings'] = [tm10.ContentBinding(cb) for cb in content_bindings]

            request_parameters['delivery_parameters'] = delivery_parameters

        request = tm10.ManageFeedSubscriptionRequest(**request_parameters)
        response = self._execute_request(request, uri=uri, service_type=SVC_FEED_MANAGEMENT)

        return response


    def get_feeds(self, uri=None):

        request = tm10.FeedInformationRequest(message_id=tm10.generate_message_id())
        response = self._execute_request(request, uri=uri, service_type=SVC_FEED_MANAGEMENT)

        if response:
            return response.feed_informations


    def poll(self, feed, begin_date=None, end_date=None, subscription_id=None, uri=None):

        data = dict(
            message_id = self._generate_id(),
            feed_name = feed,
            exclusive_begin_timestamp_label = begin_date,
            inclusive_end_timestamp_label = end_date
        )

        if subscription_id:
            data['subscription_id'] = subscription_id

        request = tm10.PollRequest(**data)
        response = self._execute_request(request, uri=uri, service_type=SVC_POLL)

        for block in response.content_blocks:
            yield block

        # No poll fulfillment in TAXII 1.0


    def poll_prepared(self, feed, begin_date=None, end_date=None, subscription_id=None, uri=None):

        for block in self.poll(feed, begin_date=begin_date, end_date=end_date, subscription_id=subscription_id, uri=uri):
            #FIXME: self.host here may not be a correct host
            yield extract_content(block, source_collection=feed, source=self.host)





