import six
from six.moves import map

from . import constants as const
from .entities import (
    ContentBinding, Collection, PushMethod,
    Subscription, ServiceInstance,
    InboxDetailedService, DetailedServiceInstance, ContentBlock,
    InboxService, SubscriptionParameters, SubscriptionResponse)


def to_collection_entities(collections, version):
    return [to_collection_entity(c, version) for c in collections]


def to_collection_entity(collection, version):

    push_methods = []
    for pm in collection.push_methods:
        method = PushMethod(
            protocol=pm.push_protocol,
            message_bindings=pm.push_message_bindings
        )
        method.raw = pm
        push_methods.append(method)

    subscription_methods = []
    for sm in collection.subscription_methods:
        instance = ServiceInstance(
            protocol=sm.subscription_protocol,
            address=sm.subscription_address,
            message_bindings=sm.subscription_message_bindings
        )
        instance.raw = sm
        subscription_methods.append(instance)

    content_bindings = to_content_binding_entities(
        collection.supported_contents)

    polling_services = []
    for i in collection.polling_service_instances:
        instance = ServiceInstance(
            protocol=i.poll_protocol,
            address=i.poll_address,
            message_bindings=i.poll_message_bindings
        )
        instance.raw = i
        polling_services.append(instance)

    if version == 10:
        name = collection.feed_name
        description = collection.feed_description
        coll_type = Collection.TYPE_FEED
        volume = None
        inboxes = None

    elif version == 11:
        name = collection.collection_name
        description = collection.collection_description
        coll_type = collection.collection_type
        volume = collection.collection_volume

        inboxes = []
        for inbox in collection.receiving_inbox_services:
            inboxes.append(InboxService(
                protocol=inbox.inbox_protocol,
                address=inbox.inbox_address,
                message_bindings=inbox.inbox_message_bindings,
                content_bindings=to_content_binding_entities(
                    inbox.supported_contents)
            ))

    collection_entity = Collection(
        name=name,
        description=description,
        type=coll_type,
        available=collection.available,
        push_methods=push_methods,
        subscription_methods=subscription_methods,
        content_bindings=content_bindings,
        polling_services=polling_services,
        volume=volume,
        receiving_inboxes=inboxes
    )
    collection_entity.raw = collection

    return collection_entity


def to_content_binding_entity(raw_binding):

    if isinstance(raw_binding, six.string_types):
        binding = ContentBinding(raw_binding)
    else:
        binding = ContentBinding(
            id=raw_binding.binding_id,
            subtypes=raw_binding.subtype_ids)

    binding.raw = raw_binding
    return binding


def to_content_binding_entities(raw_bindings):
    return list(map(to_content_binding_entity, raw_bindings))


def to_detailed_service_instance_entity(service):

    params = dict(
        type=service.service_type,
        version=service.services_version,
        protocol=service.protocol_binding,
        address=service.service_address,
        message_bindings=service.message_bindings,
        available=service.available,
        message=service.message
    )

    if service.service_type == const.SVC_INBOX:
        cls = InboxDetailedService

        params['content_bindings'] = to_content_binding_entities(
            service.inbox_service_accepted_content)
    else:
        cls = DetailedServiceInstance

    instance = cls(**params)
    instance.raw = service

    return instance


def convert_to_bytes(content):
    if isinstance(content, six.text_type):
        return content.encode('utf-8')
    return content


def to_content_block_entity(block):
    b = ContentBlock(
        content=convert_to_bytes(block.content),
        content_binding=to_content_binding_entity(block.content_binding),
        timestamp=block.timestamp_label,
    )
    b.raw = block
    return b


def to_subscription_entity(subscription, version):

    params = dict(
        subscription_id=subscription.subscription_id,
    )

    params['poll_instances'] = []
    for i in subscription.poll_instances:
        instance = ServiceInstance(
            protocol=i.poll_protocol,
            address=i.poll_address,
            message_bindings=i.poll_message_bindings
        )
        instance.raw = i
        params['poll_instances'].append(instance)

    raw_delivery_parameters = (
        subscription.delivery_parameters
        if version == 10 else subscription.push_parameters)

    if raw_delivery_parameters:
        if version == 10:
            bindings = to_content_binding_entities(
                raw_delivery_parameters.content_bindings)
        else:
            bindings = None

        _message_bindings = [raw_delivery_parameters.delivery_message_binding]

        parameters = InboxService(
            address=raw_delivery_parameters.inbox_address,
            protocol=raw_delivery_parameters.inbox_protocol,
            message_bindings=_message_bindings,
            content_bindings=bindings
        )
        parameters.raw = raw_delivery_parameters
        params['delivery_parameters'] = parameters

    if version == 11:
        sp = subscription.subscription_parameters
        parameters = SubscriptionParameters(
            response_type=sp.response_type,
            content_bindings=to_content_binding_entities(sp.content_bindings)
        )
        parameters.raw = sp
        params.update({
            'subscription_parameters': parameters,
            'status': subscription.status
        })

    entity = Subscription(**params)
    entity.raw = subscription
    return entity


def to_subscription_response_entity(raw_response, version):
    subscriptions = []
    for s in raw_response.subscription_instances:
        subscriptions.append(to_subscription_entity(s, version))

    collection_name = (raw_response.collection_name
                       if version == 11 else raw_response.feed_name)

    response = SubscriptionResponse(
        collection_name=collection_name,
        message=raw_response.message,
        subscriptions=subscriptions
    )
    response.raw = raw_response
    return response
