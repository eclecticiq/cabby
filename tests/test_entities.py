import pytest

from cabby import entities


@pytest.mark.parametrize('obj, expected', [
    (
        entities.ContentBlockCount(count=10, is_partial=False),
        'ContentBlockCount(count=10, is_partial=False)',
    ),
    (
        entities.Collection(name='test', description='not today'),
        'Collection(name=test, type=DATA_FEED, available=None)',
    ),
    (
        entities.ContentBinding(id=17),
        'ContentBinding(id=17, subtypes=[])',
    ),
    (
        entities.ServiceInstance(
            protocol='http', address='eiq', message_bindings=[],
        ),
        'ServiceInstance(protocol=http, address=eiq)',
    ),
    (
        entities.InboxService(
            protocol='http', address='eiq', message_bindings=[],
        ),
        'InboxService(protocol=http, address=eiq)',
    ),
    (
        entities.PushMethod(protocol='http', message_bindings=[]),
        'PushMethod(protocol=http)',
    ),
    (
        entities.SubscriptionParameters(response_type='FULL'),
        'SubscriptionParameters(response_type=FULL)',
    ),
    (
        entities.DetailedServiceInstance(
            type='test', version='urn:taxii.mitre.org:services:1.0',
            protocol='https', address='eiq', message_bindings=[]),
        'DetailedServiceInstance(type=test, address=eiq)',
    ),
    (
        entities.InboxDetailedService(
            type='test', version='urn:taxii.mitre.org:services:1.0',
            protocol='https', address='eiq',
            message_bindings=[], content_bindings=[]),
        'InboxDetailedService(type=test, address=eiq)',
    ),
    (
        entities.ContentBlock(content='', content_binding=[], timestamp=123),
        'ContentBlock(timestamp=123)',
    ),
    (
        entities.SubscriptionResponse(collection_name='eiq'),
        'SubscriptionResponse(collection_name=eiq)',
    ),
    (
        entities.Subscription(subscription_id=456),
        'Subscription(subscription_id=456, status=UNKNOWN)',
    ),
])
def test_repr(obj, expected):
    assert repr(obj) == expected
