
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


    def push(self, content, content_binding, subtype=None, collections=[], uri=None):

        if subtype:
            self.log.warn('Subtype is not supported in TAXII version %s. Ignoring', self.taxii_version)

        if collections:
            self.log.warn('Destination collections are not supported in TAXII version %s. Ignoring', self.taxii_version)


        content_block = tm10.ContentBlock(content_binding, content)
        inbox_message = tm10.InboxMessage(message_id=self._generate_message_id(), content_blocks=[content_block])

        response = self._execute_request(inbox_message, uri=uri, service_type=SVC_INBOX)

        if response:
            self.log.info("Content successfully pushed")


    def get_feeds(self, uri=None):

        request = tm10.FeedInformationRequest(message_id=tm10.generate_message_id())
        response = self._execute_request(request, uri=uri, service_type=SVC_FEED_MANAGEMENT)

        return response


    def poll(self, feed, begin_date=None, end_date=None, subscription=None, uri=None):

        data = dict(
            message_id = self._generate_id(),
            feed_name = feed,
            exclusive_begin_timestamp_label = begin_date,
            inclusive_end_timestamp_label = end_date
        )

        if subscription:
            data['subscription_id'] = subscription_id

        request = tm10.PollRequest(**data)
        response = self._execute_request(request, uri=uri, service_type=SVC_POLL)

        for block in extract_content(response, source=self.host, source_collection=feed):
            yield block

        # No poll fulfillment in TAXII 1.0
