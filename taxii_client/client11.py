from datetime import datetime

import libtaxii.messages_11 as tm11
from libtaxii.constants import *

from .abstract import AbstractClient


class Client11(AbstractClient):

    taxii_version = VID_TAXII_XML_11


    def _discovery_request(self, uri):
        request = tm11.DiscoveryRequest(message_id=self._generate_id())
        response = self._execute_request(request, uri=uri)
        return response


    def __subscription_status_request(self, action, collection, subscription_id=None, uri=None):
        request_parameters = dict(
            message_id = self._generate_id(),
            action = action,
            collection_name = collection,
            subscription_id = subscription_id
        )

        request = tm11.ManageCollectionSubscriptionRequest(**request_parameters)
        response = self._execute_request(request, uri=uri, service_type=SVC_COLLECTION_MANAGEMENT)

        return response

    
    def get_subscription_status(self, collection, subscription_id=None, uri=None):

        return self.__subscription_status_request(ACT_STATUS, collection,
                subscription_id=subscription_id, uri=uri)


    def pause_subscription(self, collection, subscription_id=None, uri=None):

        return self.__subscription_status_request(ACT_PAUSE, collection,
                subscription_id=subscription_id, uri=uri)


    def resume_subscription(self, collection, subscription_id=None, uri=None):

        return self.__subscription_status_request(ACT_RESUME, collection,
                subscription_id=subscription_id, uri=uri)


    def unsubscribe(self, collection, subscription_id=None, uri=None):

        return self.__subscription_status_request(ACT_UNSUBSCRIBE, collection,
                subscription_id=subscription_id, uri=uri)


    def subscribe(self, collection, count_only=False, inbox_service=None, content_bindings=None, uri=None):

        subscription_params = tm11.SubscriptionParameters(
            response_type = RT_COUNT_ONLY if count_only else RT_FULL,
        )

        if content_bindings:
            subscription_params['content_bindings'] = [tm11.ContentBinding(cb) for cb in content_bindings]

        request_parameters = dict(
            message_id = self._generate_id(),
            action = ACT_SUBSCRIBE,
            collection_name = collection,
            subscription_parameters = subscription_params,
        )

        if inbox_service:
            request_parameters['push_parameters'] = tm11.PushParameters(
                inbox_protocol = inbox_service.protocol_binding,
                inbox_address = inbox_service.service_address,
                delivery_message_binding = inbox_service.message_bindings[0] if inbox_service.message_bindings else ''
            )

        request = tm11.ManageCollectionSubscriptionRequest(**request_parameters)
        response = self._execute_request(request, uri=uri, service_type=SVC_COLLECTION_MANAGEMENT)

        return response


    def get_collections(self, uri=None):

        request = tm11.CollectionInformationRequest(message_id=self._generate_id())
        response = self._execute_request(request, uri=uri, service_type=SVC_COLLECTION_MANAGEMENT)

        return response


    def push(self, content, content_binding, subtype=None, collections=[], uri=None):

        content_block = tm11.ContentBlock(tm11.ContentBinding(content_binding), content)

        if subtype:
            content_block.content_binding.subtype_ids.append(subtype)

        inbox_message = tm11.InboxMessage(message_id=self._generate_id(), content_blocks=[content_block])

        if collections:
            inbox_message.destination_collection_names.extend(collections)

        response = self._execute_request(inbox_message, uri=uri, service_type=SVC_INBOX)

        self.log.info("Content successfully pushed")


    def poll(self, collection, begin_date=None, end_date=None, count_only=False,
            subscription_id=None, inbox_service=None, uri=None):

        data = dict(
            message_id = self._generate_id(),
            collection_name = collection,
            exclusive_begin_timestamp_label = begin_date,
            inclusive_end_timestamp_label = end_date
        )

        if subscription_id:
            data['subscription_id'] = subscription_id
        else:
            poll_params = dict()

            if inbox_service:
                poll_params['delivery_parameters'] = tm11.DeliveryParameters(
                    inbox_protocol = inbox_service.protocol_binding,
                    inbox_address = inbox_service.service_address,
                    delivery_message_binding = inbox_service.message_bindings[0] if inbox_service.message_bindings else []
                )
                poll_params['allow_asynch'] = True

            if count_only:
                poll_params['response_type'] = RT_COUNT_ONLY

            data['poll_parameters'] = tm11.PollRequest.PollParameters(**poll_params)

        request = tm11.PollRequest(**data)

        response = self._execute_request(request, uri=uri, service_type=SVC_POLL)

        for block in response.content_blocks:
            yield block

        while response.more:
            part = response.result_part_number + 1
            for block in self.fulfilment(collection, response.result_id, part_number=part, uri=uri):
                yield block


    def poll_prepared(self, collection, begin_date=None, end_date=None, subscription_id=None, uri=None):

        for block in self.poll(collection, begin_date=begin_date, end_date=end_date,
                subscription_id=subscription_id, uri=uri):
            #FIXME: self.host here may not be a correct host
            yield extract_content(block, source=self.host, source_collection=collection)


    def fulfilment(self, collection, result_id, part_number=1, uri=None, service=None):

        request = tm11.PollFulfillmentRequest(
            message_id = self._generate_id(),
            collection_name = collection,
            result_id = result_id,
            result_part_number = part_number
        )

        response = self._execute_request(request, uri=uri, service_type=SVC_POLL)

        for block in response.content_blocks:
            yield block


