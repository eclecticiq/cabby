# flake8: noqa

HOST = 'example.localhost'

DISCOVERY_PATH = '/some/discovery/path'
DISCOVERY_URI_HTTP = "http://%s%s" % (HOST, DISCOVERY_PATH)
DISCOVERY_URI_HTTPS = "https://%s%s" % (HOST, DISCOVERY_PATH)

FEED_MANAGEMENT_PATH = '/some/feeds/path'
FEED_MANAGEMENT_URI = "http://%s%s" % (HOST, FEED_MANAGEMENT_PATH)

INBOX_PATH = '/some/inbox/path'
INBOX_URI = "http://%s%s" % (HOST, INBOX_PATH)

POLL_PATH = '/some/poll/path'
POLL_URI = "http://%s%s" % (HOST, POLL_PATH)

POLL_FEED = "some-feed"

CONTENT = '_content_'
CONTENT_BINDING = '_binding_'
CONTENT_BLOCKS = ("Content Block A", "Content Block B")

SUBSCRIPTION_ID = 'some-subscription-id-123'

DISCOVERY_RESPONSE = '''
<taxii:Discovery_Response xmlns:taxii="http://taxii.mitre.org/messages/taxii_xml_binding-1" xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:tdq="http://taxii.mitre.org/query/taxii_default_query-1" message_id="2978" in_response_to="63360">
    <taxii:Service_Instance service_type="INBOX" service_version="urn:taxii.mitre.org:services:1.1" available="true">
        <taxii:Protocol_Binding>urn:taxii.mitre.org:protocol:http:1.0</taxii:Protocol_Binding>
        <taxii:Address>%(inbox_uri)s</taxii:Address>
        <taxii:Message>TAXII Inbox Service</taxii:Message>
        <taxii:Message_Binding>urn:taxii.mitre.org:message:xml:1.1</taxii:Message_Binding>
    </taxii:Service_Instance>
    <taxii:Service_Instance service_type="DISCOVERY" service_version="urn:taxii.mitre.org:services:1.1" available="true">
        <taxii:Protocol_Binding>urn:taxii.mitre.org:protocol:http:1.0</taxii:Protocol_Binding>
        <taxii:Address>%(discovery_uri)s</taxii:Address>
        <taxii:Message>TAXII Discovery Service</taxii:Message>
    </taxii:Service_Instance>
    <taxii:Service_Instance service_type="FEED_MANAGEMENT" service_version="urn:taxii.mitre.org:services:1.1" available="true">
        <taxii:Protocol_Binding>urn:taxii.mitre.org:protocol:https:1.0</taxii:Protocol_Binding>
        <taxii:Address>%(feed_management_uri)s</taxii:Address>
        <taxii:Message_Binding>urn:taxii.mitre.org:message:xml:1.1</taxii:Message_Binding>
    </taxii:Service_Instance>
    <taxii:Service_Instance service_type="DISCOVERY" service_version="urn:taxii.mitre.org:services:1.1" available="true">
        <taxii:Protocol_Binding>urn:taxii.mitre.org:protocol:http:1.0</taxii:Protocol_Binding>
        <taxii:Address>example2.com/taxii-discovery-service</taxii:Address>
        <taxii:Message>Example2 TAXII Discovery Service</taxii:Message>
    </taxii:Service_Instance>
</taxii:Discovery_Response>
''' % dict(inbox_uri=INBOX_URI, discovery_uri=DISCOVERY_URI_HTTP, feed_management_uri=FEED_MANAGEMENT_URI)



FEED_MANAGEMENT_RESPONSE = '''
<taxii:Feed_Information_Response xmlns:taxii="http://taxii.mitre.org/messages/taxii_xml_binding-1" xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:tdq="http://taxii.mitre.org/query/taxii_default_query-1" message_id="5080" in_response_to="89246">
    <taxii:Feed feed_name="%(feed_name)s" available="true">
        <taxii:Description>%(feed_name)s</taxii:Description>
        <taxii:Content_Binding>urn:stix.mitre.org:xml:1.0</taxii:Content_Binding>
        <taxii:Polling_Service>
            <taxii:Protocol_Binding>urn:taxii.mitre.org:protocol:https:1.0</taxii:Protocol_Binding>
            <taxii:Address>%(poll_uri)s</taxii:Address>
            <taxii:Message_Binding>urn:taxii.mitre.org:message:xml:1.1</taxii:Message_Binding>
        </taxii:Polling_Service>
    </taxii:Feed>
    <taxii:Feed feed_name="anotherone" available="true">
        <taxii:Description>Another feed</taxii:Description>
        <taxii:Content_Binding>urn:stix.mitre.org:xml:1.0</taxii:Content_Binding>
        <taxii:Polling_Service>
            <taxii:Protocol_Binding>urn:taxii.mitre.org:protocol:https:1.0</taxii:Protocol_Binding>
            <taxii:Address>%(poll_uri)s</taxii:Address>
            <taxii:Message_Binding>urn:taxii.mitre.org:message:xml:1.1</taxii:Message_Binding>
        </taxii:Polling_Service>
    </taxii:Feed>
</taxii:Feed_Information_Response>
''' % dict(feed_name=POLL_FEED, poll_uri=POLL_URI)



POLL_RESPONSE = '''
<taxii:Poll_Response xmlns:taxii="http://taxii.mitre.org/messages/taxii_xml_binding-1" xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:tdq="http://taxii.mitre.org/query/taxii_default_query-1" message_id="37911" in_response_to="51737" feed_name="%(feed_name)s">
    <taxii:Inclusive_End_Timestamp>2015-01-23T16:26:22.706007+00:00</taxii:Inclusive_End_Timestamp>
    <taxii:Content_Block>
        <taxii:Content_Binding>urn:stix.mitre.org:xml:1.1.1</taxii:Content_Binding>
        <taxii:Content>%(block_1)s</taxii:Content>
        <taxii:Timestamp_Label>2015-01-22T15:28:49.947928+00:00</taxii:Timestamp_Label>
    </taxii:Content_Block>
    <taxii:Content_Block>
        <taxii:Content_Binding>urn:stix.mitre.org:xml:1.1.1</taxii:Content_Binding>
        <taxii:Content>%(block_2)s</taxii:Content>
        <taxii:Timestamp_Label>2015-01-25T15:28:49.947928+00:00</taxii:Timestamp_Label>
    </taxii:Content_Block>
</taxii:Poll_Response>
''' % dict(feed_name=POLL_FEED, block_1=CONTENT_BLOCKS[0], block_2=CONTENT_BLOCKS[1])

SUBSCRIPTION_RESPONSE = '''
<taxii:Subscription_Management_Response xmlns:taxii="http://taxii.mitre.org/messages/taxii_xml_binding-1" xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:tdq="http://taxii.mitre.org/query/taxii_default_query-1" message_id="123123" in_response_to="345345" feed_name="%(feed_name)s">
    <taxii:Subscription subscription_id="%(subscription_id)s">
        <taxii:Delivery_Parameters>
            <taxii:Protocol_Binding>urn:taxii.mitre.org:protocol:https:1.0</taxii:Protocol_Binding>
            <taxii:Address>%(inbox_uri)s</taxii:Address>
            <taxii:Message_Binding>urn:taxii.mitre.org:message:xml:1.1</taxii:Message_Binding>
            <taxii:Content_Binding>%(content_binding)s</taxii:Content_Binding>
        </taxii:Delivery_Parameters>
        <taxii:Poll_Instance>
            <taxii:Protocol_Binding>urn:taxii.mitre.org:protocol:https:1.0</taxii:Protocol_Binding>
            <taxii:Address>%(poll_uri)s</taxii:Address>
            <taxii:Message_Binding>urn:taxii.mitre.org:message:xml:1.1</taxii:Message_Binding>
        </taxii:Poll_Instance>
    </taxii:Subscription>
</taxii:Subscription_Management_Response>
''' % dict(subscription_id=SUBSCRIPTION_ID, poll_uri=POLL_URI, inbox_uri=INBOX_URI, feed_name=POLL_FEED,
        content_binding=CONTENT_BINDING)


INBOX_RESPONSE = '''
<taxii:Status_Message xmlns:taxii="http://taxii.mitre.org/messages/taxii_xml_binding-1" xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:tdq="http://taxii.mitre.org/query/taxii_default_query-1" message_id="48205" in_response_to="13777" status_type="SUCCESS"/>
'''

STATUS_MESSAGE_UNAUTHORIZED = """\
<?xml version="1.0"?>
<taxii:Status_Message
    xmlns:taxii="http://taxii.mitre.org/messages/taxii_xml_binding-1"
    xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1"
    xmlns:tdq="http://taxii.mitre.org/query/taxii_default_query-1"
    message_id="123123"
    in_response_to="0"
    status_type="UNAUTHORIZED"/>
"""
