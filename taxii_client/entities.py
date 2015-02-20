
from libtaxii.constants import *

class Collection(object):

    TYPE_FEED = CT_DATA_FEED
    TYPE_SET = CT_DATA_SET

    version = None

    def __init__(self, name, description, type=TYPE_FEED, available=None,
            push_methods=[], content_bindings=[], polling_services=[],
            subscription_methods=[], receiving_inboxes=[], collection_volume=None):

        self.name = name
        self.description = description
        self.type = type

        self.available = available

        self.content_bindings = content_bindings or []
        self.push_methods = push_methods or []

        self.polling_services = polling_services or []
        self.subscription_methods = subscription_methods or []


    @staticmethod
    def to_entity_10(collection):
        return Collection.to_entity(collection, version=10)

    @staticmethod
    def to_entity(collection, version):

        push_methods = []
        for pm in collection.push_methods:
            push_methods.append(PushMethod(
                protocol = pm.push_protocol,
                message_bindings = pm.push_message_bindings
            ))

        subscription_methods = []
        for sm in collection.subscription_methods:
            subscription_methods.append(ServiceInstance(
                protocol = sm.subscription_protocol,
                address = sm.subscription_address,
                message_bindings = sm.subscription_message_bindings
            ))

        content_bindings = map(ContentBinding, collection.supported_contents)

        polling_services = []
        for sm in collection.polling_service_instances:
            polling_services.append(ServiceInstance(
                protocol = sm.poll_protocol,
                address = sm.poll_address,
                message_bindings = sm.poll_message_bindings
            ))

        if version == 10:
            name = collection.feed_name
            description = collection.feed_description
            coll_type = Collection.TYPE_FEED
        elif version == 11:
            name = collection.collection_name
            description = collection.collection_description
            coll_type = collection.collection_type

        return Collection(
            name = name,
            description = description,
            type = coll_type,
            available = collection.available,
            push_methods = push_methods,
            subscription_methods = subscription_methods,
            content_bindings = content_bindings,
            polling_services = polling_services
        )



class PushMethod(object):

    def __init__(self, protocol, message_bindings):
        self.protocol = protocol
        self.message_bindings = message_bindings


class ContentBinding(object):

    def __init__(self, id, subtypes=[]):
        self.id = id
        self.subtypes = subtypes

    @staticmethod
    def to_entity(raw_binding):

        if isinstance(raw_binding, basestring):
            return ContentBinding(raw_binding)
        else:
            return ContentBinding(
                id = raw_binding.binding_id,
                subtypes = raw_binding.subtype_ids
            )



# Polling services
# Subscription methods
class ServiceInstance(object):

    def __init__(self, protocol, address, message_bindings):
        self.protocol = protocol
        self.address = address
        self.message_bindings = message_bindings


class InboxService(ServiceInstance):

    def __init__(self, protocol, address, message_bindings, content_bindings=[]):
        super(InboxService, self).__init__(protocol, address, message_bindings)

        self.content_bindings = content_bindings


class DetailedServiceInstance(object):
    '''
    Detailed description of TAXII server instance

    "Supported Query" is not supported
    '''

    VERSION_10 = VID_TAXII_SERVICES_10
    VERSION_11 = VID_TAXII_SERVICES_11

    PROTOCOL_HTTP = VID_TAXII_HTTP_10
    PROTOCOL_HTTPS = VID_TAXII_HTTPS_10

    def __init__(self, type, version, protocol, address, message_bindings,
            available=None, message=None):

        self.type = type
        self.version = version
        self.protocol = protocol
        self.address = address
        self.message_bindings = message_bindings

        self.available = available
        self.message = message


    @staticmethod
    def to_entity(service):

        params = dict(
            type = service.service_type,
            version = service.services_version,
            protocol = service.protocol_binding,
            address = service.service_address,
            message_bindings = service.message_bindings,
            available = service.available,
            message = service.message
        )

        if service.service_type == SVC_INBOX:
            cls = InboxDetailedService

            params['content_bindings'] = map(ContentBinding.to_entity, 
                    service.inbox_service_accepted_content)
        else:
            cls = DetailedServiceInstance

        return cls(**params)


class InboxDetailedService(DetailedServiceInstance):

    def __init__(self, content_bindings, **kwargs):
        super(InboxDetailedService, self).__init__(**kwargs)

        self.content_bindings = content_bindings


class ContentBlock(object):
    
    def __init__(self, content, content_binding, timestamp):

        self.content = content
        self.binding = content_binding
        self.timestamp = timestamp


    @staticmethod
    def to_entity(block):
        return ContentBlock(
            content = block.content,
            content_binding = ContentBinding.to_entity(block.content_binding),
            timestamp = block.timestamp_label,
        )
