import logging

from . import constants as const


log = logging.getLogger(__name__)

SERVICE_TYPES = set(const.SVC_TYPES)


class Entity(object):
    '''Generic entity.'''
    raw = None


class ContentBlockCount(Entity):
    '''Content Block count.

    Represents an amount of content blocks in a poll query result.

    :param int count: amount of content blocks in a poll query result.
    :param bool is_partial:
           indicates whether the provided Record Count is the exact number
           of applicable records, or if the provided number is a lower bound
           and there may be more records than stated.
    '''
    def __init__(self, count, is_partial=False):
        self.count = count
        self.is_partial = is_partial

    def __repr__(self):
        t = '{cls}(count={count}, is_partial={is_partial})'
        return t.format(cls=type(self).__name__, **vars(self))


class Collection(Entity):
    '''Collection entity.

    Represents TAXII Collection and TAXII Feed objects.

    :param str name: name of the collection
    :param str description: description message
    :param str type: type of a collection. Supported values are
           :attr:`TYPE_FEED` and :attr:`TYPE_SET`
    :param bool available: if a collection marked as available
    :param list push_methods: availavle push methods for a collection,
           a list of :py:class:`cabby.entities.PushMethods`
    :param list content_bindings: a list of
           :py:class:`cabby.entities.ContentBinding`
    :param list polling_services: a list of
           :py:class:`cabby.entities.ServiceInstance`
    :param list subscription_methods: a list of
           :py:class:`cabby.entities.ServiceInstance`
    :param list receiving_inboxes: a list of
           :py:class:`cabby.entities.InboxService`
    :param int volume: collection's volume
    '''

    TYPE_FEED = const.CT_DATA_FEED
    TYPE_SET = const.CT_DATA_SET

    def __init__(self, name, description, type=TYPE_FEED, available=None,
                 push_methods=None, content_bindings=None,
                 polling_services=None, subscription_methods=None,
                 receiving_inboxes=None, volume=None):

        if type not in [self.TYPE_FEED, self.TYPE_SET]:
            log.error("Unknown collection type: %s", type)

        self.name = name
        self.description = description
        self.type = type

        self.available = available

        self.content_bindings = content_bindings or []
        self.push_methods = push_methods or []

        self.polling_services = polling_services or []
        self.subscription_methods = subscription_methods or []

        self.receiving_inboxes = receiving_inboxes or []
        self.volume = volume

    def __repr__(self):
        t = '{cls}(name={name}, type={type}, available={available})'
        return t.format(cls=type(self).__name__, **vars(self))


class ContentBinding(Entity):
    '''Content Binding entity.

    Represents TAXII Content Binding.

    :param str id: Content Binding ID
    :param list subtypes: Content Subtypes IDs
    '''

    def __init__(self, id, subtypes=None):
        self.id = id
        self.subtypes = subtypes or []

    def __repr__(self):
        t = '{cls}(id={id}, subtypes={subtypes})'
        return t.format(cls=type(self).__name__, **vars(self))


class ServiceInstance(Entity):
    '''Generic TAXII Service entity.

    :param str protocol: service Protocol Binding value
    :param str address: service network address
    :param list message_bindings: service Message Bindings,
                                  as list of strings
    '''

    def __init__(self, protocol, address, message_bindings):
        self.protocol = protocol
        self.address = address
        self.message_bindings = message_bindings

    def __repr__(self):
        t = '{cls}(protocol={protocol}, address={address})'
        return t.format(cls=type(self).__name__, **vars(self))


class InboxService(ServiceInstance):
    '''Inbox Service entity.

    Represents TAXII Inbox Service.

    :param str protocol: service Protocol Binding value
    :param str address: service network address
    :param list message_bindings: service Message Bindings, as list of strings
    :param list content_bindings: a list of
                :py:class:`cabby.entities.ContentBinding`
    '''

    def __init__(self, protocol, address, message_bindings,
                 content_bindings=None):

        super(InboxService, self).__init__(protocol, address, message_bindings)

        self.content_bindings = content_bindings or []


class PushMethod(Entity):
    '''Push Method entity.

    Represents TAXII Push Method.

    :param str protocol: service Protocol Binding value
    :param list message_bindings: service Message Bindings, as list of strings
    '''

    def __init__(self, protocol, message_bindings):
        self.protocol = protocol
        self.message_bindings = message_bindings

    def __repr__(self):
        t = '{cls}(protocol={protocol})'
        return t.format(cls=type(self).__name__, **vars(self))


class SubscriptionParameters(Entity):
    '''Subscription Parameters Entity.

    Represents TAXII Subscription Parameters.

    :param str response_type: response type. Supported values are
               :attr:`TYPE_FULL` and :attr:`TYPE_COUNTS`
    :param list content_bindings: a list of
               :py:class:`cabby.entities.ContentBinding`
    '''

    TYPE_FULL = const.RT_FULL
    TYPE_COUNT = const.RT_COUNT_ONLY

    def __init__(self, response_type, content_bindings=None):
        if response_type not in [self.TYPE_FULL, self.TYPE_COUNT]:
            log.error("Unknown response type: %s", response_type)
        self.response_type = response_type
        self.content_bindings = content_bindings or []

    def __repr__(self):
        t = '{cls}(response_type={response_type})'
        return t.format(cls=type(self).__name__, **vars(self))


class DetailedServiceInstance(Entity):
    '''Detailed description of a generic TAXII Service instance

    :param str type: service type. Supported values are
                        in :py:data:`cabby.entities.SERVICE_TYPES`
    :param str version: service version. Supported values are
                        :attr:`VERSION_10` and :attr:`VERSION_11`
    :param str protocol: service Protocol Binding value
    :param str address: service network address
    :param list message_bindings: service Message Bindings, as list of strings
    :param bool available: if service is marked as available
    :param str message: message attached to a service
    '''

    VERSION_10 = const.TAXII_SERVICES_10
    VERSION_11 = const.TAXII_SERVICES_11

    PROTOCOL_HTTP = const.PROTOCOL_HTTP_10_BINDING
    PROTOCOL_HTTPS = const.PROTOCOL_HTTPS_10_BINDING

    def __init__(self, type, version, protocol, address, message_bindings,
                 available=None, message=None):

        if version not in [self.VERSION_10, self.VERSION_11]:
            log.error("Unknown service version: %s", version)
        if protocol not in [self.PROTOCOL_HTTP, self.PROTOCOL_HTTPS]:
            log.error("Unknown service protocol: %s", protocol)

        self.type = type
        self.version = version
        self.protocol = protocol
        self.address = address
        self.message_bindings = message_bindings

        self.available = available
        self.message = message

    def __repr__(self):
        t = '{cls}(type={type}, address={address})'
        return t.format(cls=type(self).__name__, **vars(self))


class InboxDetailedService(DetailedServiceInstance):
    '''Detailed description of TAXII Inbox Service.

    :param str type: service type. Supported values are
                     in :py:data:`cabby.entities.SERVICE_TYPES`
    :param str version: service version. Supported values are
                        :attr:`VERSION_10` and :attr:`VERSION_11`
    :param str protocol: service Protocol Binding value
    :param str address: service network address
    :param list message_bindings: service Message Bindings, as list of strings
    :param list content_bindings: a list of
                                  :py:class:`cabby.entities.ContentBinding`
    :param bool available: if service is marked as available
    :param str message: message attached to a service
    '''

    def __init__(self, content_bindings, **kwargs):
        super(InboxDetailedService, self).__init__(**kwargs)
        self.content_bindings = content_bindings


class ContentBlock(Entity):
    '''Content Block entity.

    Represents TAXII Content Block.

    :param str content: TAXII message payload
    :param `cabby.entities.ContentBinding` content_binding: Content Binding
    :param datetime timestamp: content block timestamp label
    '''

    def __init__(self, content, content_binding, timestamp):
        self.content = content
        self.binding = content_binding
        self.timestamp = timestamp

    def __repr__(self):
        t = '{cls}(timestamp={timestamp})'
        return t.format(cls=type(self).__name__, **vars(self))


class SubscriptionResponse(Entity):
    '''Subscription Response entity.

    :param str collection_name: collection name
    :param str message: message attached to Subscription Response
    :param list subscriptions: a list of `cabby.entities.Subscription`
    '''

    def __init__(self, collection_name, message=None, subscriptions=None):
        self.collection_name = collection_name
        self.message = message
        self.subscriptions = subscriptions or []

    def __repr__(self):
        t = '{cls}(collection_name={collection_name})'
        return t.format(cls=type(self).__name__, **vars(self))


class Subscription(Entity):
    '''Subscription entity.

    :param str subscription_id: subscription ID
    :param str status: subscription status. Supported values are
                 :attr:`STATUS_UNKNOWN`, :attr:`STATUS_ACTIVE`,
                 :attr:`STATUS_PAUSED`, :attr:`STATUS_UNSUBSCRIBED`
    :param list delivery_parameters: a list of `cabby.entities.InboxService`
    :param list subscription_parameters:
                a list of `cabby.entities.SubscriptionParameters`
    :param list poll_instances: a list of `cabby.entities.ServiceInstance`
    '''
    STATUS_UNKNOWN = 'UNKNOWN'
    STATUS_ACTIVE = const.SS_ACTIVE
    STATUS_PAUSED = const.SS_PAUSED
    STATUS_UNSUBSCRIBED = const.SS_UNSUBSCRIBED

    def __init__(self, subscription_id, status=STATUS_UNKNOWN,
                 delivery_parameters=None, subscription_parameters=None,
                 poll_instances=None):

        assert status in [self.STATUS_UNKNOWN, self.STATUS_ACTIVE,
                          self.STATUS_PAUSED, self.STATUS_UNSUBSCRIBED]

        self.id = subscription_id
        self.status = status
        self.delivery_parameters = delivery_parameters
        self.subscription_parameters = subscription_parameters
        self.poll_instances = poll_instances

    def __repr__(self):
        t = '{cls}(subscription_id={id}, status={status})'
        return t.format(cls=type(self).__name__, **vars(self))
