
from libtaxii import constants as const

class Entity(object):
    raw = None

class Collection(Entity):

    TYPE_FEED = const.CT_DATA_FEED
    TYPE_SET = const.CT_DATA_SET

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



class ContentBinding(Entity):

    def __init__(self, id, subtypes=[]):
        self.id = id
        self.subtypes = subtypes


# Polling services
# Subscription methods
# Poll instances
class ServiceInstance(Entity):

    def __init__(self, protocol, address, message_bindings):
        self.protocol = protocol
        self.address = address
        self.message_bindings = message_bindings


class InboxService(ServiceInstance):

    def __init__(self, protocol, address, message_bindings, content_bindings=[]):
        super(InboxService, self).__init__(protocol, address, message_bindings)

        self.content_bindings = content_bindings


class PushMethod(Entity):
    '''
    Entity represents the protocol that TAXII server supports
    when it pushes data via subscription delivery
    '''

    def __init__(self, protocol, message_bindings):
        self.protocol = protocol
        self.message_bindings = message_bindings


class DeliveryParameters(Entity):

    def __init__(self, address, protocol, message_binding, content_bindings=[]):
        self.address = address
        self.protocol = protocol
        self.message_binding = message_binding
        self.content_bindings = content_bindings


class SubscriptionParameters(Entity):

    TYPE_FULL = const.RT_FULL
    TYPE_COUNTS = const.RT_COUNT_ONLY

    def __init__(self, response_type, content_bindings=[]):
        self.response_type = response_type
        self.content_bindings = content_bindings


class DetailedServiceInstance(Entity):
    '''
    Detailed description of TAXII server instance

    "Supported Query" is not implemented
    '''

    VERSION_10 = const.VID_TAXII_SERVICES_10
    VERSION_11 = const.VID_TAXII_SERVICES_11

    PROTOCOL_HTTP = const.VID_TAXII_HTTP_10
    PROTOCOL_HTTPS = const.VID_TAXII_HTTPS_10

    def __init__(self, type, version, protocol, address, message_bindings,
            available=None, message=None):

        self.type = type
        self.version = version
        self.protocol = protocol
        self.address = address
        self.message_bindings = message_bindings

        self.available = available
        self.message = message


class InboxDetailedService(DetailedServiceInstance):

    def __init__(self, content_bindings, **kwargs):
        super(InboxDetailedService, self).__init__(**kwargs)

        self.content_bindings = content_bindings


class ContentBlock(Entity):
    
    def __init__(self, content, content_binding, timestamp):

        self.content = content
        self.binding = content_binding
        self.timestamp = timestamp


class SubscriptionResponse(Entity):

    def __init__(self, collection_name, message=None, subscriptions=[]):

        self.collection_name = collection_name
        self.message = message
        self.subscriptions = subscriptions


class Subscription(Entity):

    STATUS_UNKNOWN = 'UNKNOWN'
    STATUS_ACTIVE = const.SS_ACTIVE
    STATUS_PAUSED = const.SS_PAUSED
    STATUS_UNSUBSCRIBED = const.SS_UNSUBSCRIBED

    def __init__(self, subscription_id, status=STATUS_UNKNOWN, delivery_parameters=None,
            subscription_parameters=None, poll_instances=None):

        self.id = subscription_id
        self.status = status
        self.delivery_parameters = delivery_parameters
        self.subscription_parameters = subscription_parameters
        self.poll_instances = poll_instances

