import libtaxii

from .abstract import AbstractClient
from .utils import extract_content

class Client10(AbstractClient):

    taxii_version = libtaxii.VID_TAXII_XML_10


    def discover_services(self, path='/services/discovery/'):

        request = tm10.DiscoveryRequest(message_id=self._generate_id())

        response = self._execute_request(request, path=path)

        self.services = response.service_instances
        return self.services


    def push(self, content, content_binding, subtype=None, collections=[], uri=None):

        if subtype:
            log.warn('Subtype is not supported in TAXII version %s. Ignoring', self.taxii_version)

        if collections:
            log.warn('Destination collections are not supported in TAXII version %s. Ignoring', self.taxii_version)


        content_block = tm10.ContentBlock(content_binding, content)
        inbox_message = tm10.InboxMessage(message_id=self._generate_message_id(), content_blocks=[content_block])

        response = self._execute_request(inbox_message, path=path)
        print response

