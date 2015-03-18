from itertools import imap

import libtaxii.messages_11 as tm11
from libtaxii import constants as const

from .abstract import AbstractClient
from .converters import (
    to_subscription_response_entity, to_content_block_entity,
    to_collection_entities
)
from .utils import pack_content_bindings


class Client11(AbstractClient):

    taxii_version = const.VID_TAXII_XML_11
    services_version = const.VID_TAXII_SERVICES_11

    def _discovery_request(self, uri):
        request = tm11.DiscoveryRequest(message_id=self._generate_id())
        response = self._execute_request(request, uri=uri)
        return response


    def __subscription_status_request(self, action, collection_name, subscription_id=None, uri=None):
        request_parameters = dict(
            message_id = self._generate_id(),
            action = action,
            collection_name = collection_name,
            subscription_id = subscription_id
        )

        request = tm11.ManageCollectionSubscriptionRequest(**request_parameters)
        response = self._execute_request(request, uri=uri, service_type=const.SVC_COLLECTION_MANAGEMENT)

        return to_subscription_response_entity(response, version=11)

    
    def get_subscription_status(self, collection_name, subscription_id=None, uri=None):

        return self.__subscription_status_request(const.ACT_STATUS, collection_name,
                subscription_id=subscription_id, uri=uri)


    def pause_subscription(self, collection_name, subscription_id, uri=None):

        return self.__subscription_status_request(const.ACT_PAUSE, collection_name,
                subscription_id=subscription_id, uri=uri)


    def resume_subscription(self, collection_name, subscription_id, uri=None):

        return self.__subscription_status_request(const.ACT_RESUME, collection_name,
                subscription_id=subscription_id, uri=uri)


    def unsubscribe(self, collection_name, subscription_id, uri=None):

        return self.__subscription_status_request(const.ACT_UNSUBSCRIBE, collection_name,
                subscription_id=subscription_id, uri=uri)


    def subscribe(self, collection_name, count_only=False, inbox_service=None, content_bindings=None, uri=None):
        '''
        content_binding - list of strings or ContentBinding entities
        '''

        sparams = tm11.SubscriptionParameters(
            response_type = const.RT_COUNT_ONLY if count_only else const.RT_FULL,
            content_bindings = pack_content_bindings(content_bindings, version=11)
        )
        rparams = dict(
            message_id = self._generate_id(),
            action = const.ACT_SUBSCRIBE,
            collection_name = collection_name,
            subscription_parameters = sparams,
        )

        if inbox_service:
            rparams['push_parameters'] = tm11.PushParameters(
                inbox_protocol = inbox_service.protocol,
                inbox_address = inbox_service.address,
                delivery_message_binding = inbox_service.message_bindings[0] if inbox_service.message_bindings else ''
            )

        request = tm11.ManageCollectionSubscriptionRequest(**rparams)
        response = self._execute_request(request, uri=uri, service_type=const.SVC_COLLECTION_MANAGEMENT)

        return to_subscription_response_entity(response, version=11)


    def get_collections(self, uri=None):

        request = tm11.CollectionInformationRequest(message_id=self._generate_id())
        response = self._execute_request(request, uri=uri, service_type=const.SVC_COLLECTION_MANAGEMENT)

        return to_collection_entities(response.collection_informations, version=11)



    def push(self, content, content_binding, subtype=None, collections_names=None, uri=None):

        content_block = tm11.ContentBlock(tm11.ContentBinding(content_binding), content)

        if subtype:
            content_block.content_binding.subtype_ids.append(subtype)

        inbox_message = tm11.InboxMessage(message_id=self._generate_id(), content_blocks=[content_block])

        if collections_names:
            inbox_message.destination_collection_names.extend(collections_names)

        response = self._execute_request(inbox_message, uri=uri, service_type=const.SVC_INBOX)

        self.log.debug("Content successfully pushed")


    def poll(self, collection_name, begin_date=None, end_date=None, count_only=False,
            subscription_id=None, inbox_service=None, content_bindings=None, uri=None):

        data = dict(
            message_id = self._generate_id(),
            collection_name = collection_name,
            exclusive_begin_timestamp_label = begin_date,
            inclusive_end_timestamp_label = end_date
        )

        if subscription_id:
            data['subscription_id'] = subscription_id
        else:
            poll_params = {
                'content_bindings' : pack_content_bindings(content_bindings, version=11)
            }

            if inbox_service:
                message_bindings = inbox_service.message_bindings[0] \
                        if inbox_service.message_bindings else []

                poll_params['delivery_parameters'] = tm11.DeliveryParameters(
                    inbox_protocol = inbox_service.protocol,
                    inbox_address = inbox_service.address,
                    delivery_message_binding = message_bindings
                )
                poll_params['allow_asynch'] = True

            if count_only:
                poll_params['response_type'] = const.RT_COUNT_ONLY

            data['poll_parameters'] = tm11.PollRequest.PollParameters(**poll_params)

        request = tm11.PollRequest(**data)
        response = self._execute_request(request, uri=uri, service_type=const.SVC_POLL)

        for block in imap(to_content_block_entity, response.content_blocks):
            yield block

        while response.more:
            part = response.result_part_number + 1
            for block in self.fulfilment(collection_name, response.result_id, part_number=part, uri=uri):
                yield block


    def fulfilment(self, collection_name, result_id, part_number=1, uri=None):

        request = tm11.PollFulfillmentRequest(
            message_id = self._generate_id(),
            collection_name = collection_name,
            result_id = result_id,
            result_part_number = part_number
        )

        response = self._execute_request(request, uri=uri, service_type=const.SVC_POLL)

        for block in imap(to_content_block_entity, response.content_blocks):
            yield block


