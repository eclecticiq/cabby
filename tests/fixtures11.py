
HOST = 'example.com'

DISCOVERY_PATH = '/some/discovery/path'
DISCOVERY_URI_HTTP = "http://%s%s" % (HOST, DISCOVERY_PATH)
DISCOVERY_URI_HTTPS = "https://%s%s" % (HOST, DISCOVERY_PATH)

COLLECTION_MANAGEMENT_PATH = '/some/collections/path'
COLLECTION_MANAGEMENT_URI = "http://%s%s" % (HOST, COLLECTION_MANAGEMENT_PATH)

INBOX_PATH = '/some/inbox/path'
INBOX_URI = "http://%s%s" % (HOST, INBOX_PATH)

POLL_PATH = '/some/poll/path'
POLL_URI = "http://%s%s" % (HOST, POLL_PATH)
POLL_COLLECTION = "some-collection"

CONTENT = '_content_'
CONTENT_BINDING = '_binding_'
CONTENT_BLOCKS = ("Content Block A", "Content Block B")

SUBSCRIPTION_ID = 'some-subscription-id-123'


DISCOVERY_RESPONSE = '''
<taxii_11:Discovery_Response xmlns:taxii="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:tdq="http://taxii.mitre.org/query/taxii_default_query-1.1" message_id="69391" in_response_to="69261">
    <taxii_11:Service_Instance service_type="INBOX" service_version="urn:taxii.mitre.org:services:1.1" available="true">
        <taxii_11:Protocol_Binding>urn:taxii.mitre.org:protocol:http:1.0</taxii_11:Protocol_Binding>
        <taxii_11:Address>%(inbox_uri)s</taxii_11:Address>
        <taxii_11:Message>TAXII Inbox Service</taxii_11:Message>
        <taxii_11:Message_Binding>urn:taxii.mitre.org:message:xml:1.1</taxii_11:Message_Binding>
    </taxii_11:Service_Instance>
    <taxii_11:Service_Instance service_type="DISCOVERY" service_version="urn:taxii.mitre.org:services:1.1" available="true">
        <taxii_11:Protocol_Binding>urn:taxii.mitre.org:protocol:http:1.0</taxii_11:Protocol_Binding>
        <taxii_11:Address>%(discovery_uri)s</taxii_11:Address>
        <taxii_11:Message>TAXII Discovery Service</taxii_11:Message>
    </taxii_11:Service_Instance>
    <taxii_11:Service_Instance xmlns:taxii="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:tdq="http://taxii.mitre.org/query/taxii_default_query-1.1" service_type="COLLECTION_MANAGEMENT" service_version="urn:taxii.mitre.org:services:1.1" available="true">
        <taxii_11:Protocol_Binding>urn:taxii.mitre.org:protocol:https:1.0</taxii_11:Protocol_Binding>
        <taxii_11:Address>%(collection_management_uri)s</taxii_11:Address>
        <taxii_11:Message_Binding>urn:taxii.mitre.org:message:xml:1.1</taxii_11:Message_Binding>
    </taxii_11:Service_Instance>
    <taxii_11:Service_Instance service_type="DISCOVERY" service_version="urn:taxii.mitre.org:services:1.1" available="true">
        <taxii_11:Protocol_Binding>urn:taxii.mitre.org:protocol:http:1.0</taxii_11:Protocol_Binding>
        <taxii_11:Address>example2.com/taxii-discovery-service</taxii_11:Address>
        <taxii_11:Message>Example2 TAXII Discovery Service</taxii_11:Message>
    </taxii_11:Service_Instance>
</taxii_11:Discovery_Response>
''' % dict(inbox_uri=INBOX_URI, discovery_uri=DISCOVERY_URI_HTTP, collection_management_uri=COLLECTION_MANAGEMENT_URI)

COLLECTION_MANAGEMENT_RESPONSE = '''
<taxii_11:Collection_Information_Response xmlns:taxii="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:tdq="http://taxii.mitre.org/query/taxii_default_query-1.1" message_id="68017" in_response_to="84459">
    <taxii_11:Collection collection_name="%(collection_name)s" collection_type="DATA_FEED" available="true">
        <taxii_11:Description>Collection %(collection_name)s</taxii_11:Description>
        <taxii_11:Content_Binding binding_id="urn:stix.mitre.org:xml:1.0"/>
        <taxii_11:Polling_Service>
            <taxii_11:Protocol_Binding>urn:taxii.mitre.org:protocol:https:1.0</taxii_11:Protocol_Binding>
            <taxii_11:Address>%(poll_uri)s</taxii_11:Address>
            <taxii_11:Message_Binding>urn:taxii.mitre.org:message:xml:1.1</taxii_11:Message_Binding>
        </taxii_11:Polling_Service>
    </taxii_11:Collection>
    <taxii_11:Collection collection_name="CollectionB" collection_type="DATA_FEED" available="true">
        <taxii_11:Description>CollectionB</taxii_11:Description>
        <taxii_11:Content_Binding binding_id="urn:stix.mitre.org:xml:1.0"/>
        <taxii_11:Polling_Service>
            <taxii_11:Protocol_Binding>urn:taxii.mitre.org:protocol:https:1.0</taxii_11:Protocol_Binding>
            <taxii_11:Address>%(poll_uri)s</taxii_11:Address>
            <taxii_11:Message_Binding>urn:taxii.mitre.org:message:xml:1.1</taxii_11:Message_Binding>
        </taxii_11:Polling_Service>
    </taxii_11:Collection>
</taxii_11:Collection_Information_Response>
''' % dict(collection_name=POLL_COLLECTION, poll_uri=POLL_URI)

POLL_RESPONSE = '''
<taxii_11:Poll_Response xmlns:taxii="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:tdq="http://taxii.mitre.org/query/taxii_default_query-1.1" message_id="375" in_response_to="65684" collection_name="%(collection_name)s" more="false" result_part_number="1">
    <taxii_11:Inclusive_End_Timestamp>2015-01-22T15:28:49.931734+00:00</taxii_11:Inclusive_End_Timestamp>
    <taxii_11:Content_Block>
        <taxii_11:Content_Binding binding_id="urn:stix.mitre.org:xml:1.1.1"/>
        <taxii_11:Content>%(block_1)s</taxii_11:Content>
        <taxii_11:Timestamp_Label>2015-01-22T15:28:49.947928+00:00</taxii_11:Timestamp_Label>
    </taxii_11:Content_Block>
    <taxii_11:Content_Block>
        <taxii_11:Content_Binding binding_id="urn:stix.mitre.org:xml:1.1.1"/>
        <taxii_11:Content>%(block_2)s</taxii_11:Content>
        <taxii_11:Timestamp_Label>2015-01-25T15:28:49.947928+00:00</taxii_11:Timestamp_Label>
    </taxii_11:Content_Block>
</taxii_11:Poll_Response>
''' % dict(collection_name=POLL_COLLECTION, block_1=CONTENT_BLOCKS[0], block_2=CONTENT_BLOCKS[1])


POLL_RESPONSE_WITH_MORE_1 = '''
<taxii_11:Poll_Response xmlns:taxii="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:tdq="http://taxii.mitre.org/query/taxii_default_query-1.1" message_id="375" in_response_to="65684" collection_name="%(collection_name)s" more="true" result_part_number="1" result_id="1">
    <taxii_11:Inclusive_End_Timestamp>2015-01-22T15:28:49.931734+00:00</taxii_11:Inclusive_End_Timestamp>
    <taxii_11:Content_Block>
        <taxii_11:Content_Binding binding_id="urn:stix.mitre.org:xml:1.1.1"/>
        <taxii_11:Content>%(block_1)s</taxii_11:Content>
        <taxii_11:Timestamp_Label>2015-01-22T15:28:49.947928+00:00</taxii_11:Timestamp_Label>
    </taxii_11:Content_Block>
</taxii_11:Poll_Response>
''' % dict(collection_name=POLL_COLLECTION, block_1=CONTENT_BLOCKS[0])


POLL_RESPONSE_WITH_MORE_2 = '''
<taxii_11:Poll_Response xmlns:taxii="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:tdq="http://taxii.mitre.org/query/taxii_default_query-1.1" message_id="375" in_response_to="65684" collection_name="%(collection_name)s" result_part_number="2">
    <taxii_11:Inclusive_End_Timestamp>2015-01-22T15:28:49.931734+00:00</taxii_11:Inclusive_End_Timestamp>
    <taxii_11:Content_Block>
        <taxii_11:Content_Binding binding_id="urn:stix.mitre.org:xml:1.1.1"/>
        <taxii_11:Content>%(block_2)s</taxii_11:Content>
        <taxii_11:Timestamp_Label>2015-01-22T15:28:49.947928+00:00</taxii_11:Timestamp_Label>
    </taxii_11:Content_Block>
</taxii_11:Poll_Response>
''' % dict(collection_name=POLL_COLLECTION, block_2=CONTENT_BLOCKS[1])


SUBSCRIPTION_RESPONSE = '''
<taxii_11:Subscription_Management_Response xmlns:taxii="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:tdq="http://taxii.mitre.org/query/taxii_default_query-1.1" message_id="SubsResp01" in_response_to="xyz" collection_name="%(collection_name)s">
    <taxii_11:Message>Some subscription message</taxii_11:Message>
    <taxii_11:Subscription status="ACTIVE">
        <taxii_11:Subscription_ID>%(subscription_id)s</taxii_11:Subscription_ID>
        <taxii_11:Subscription_Parameters>
            <taxii_11:Response_Type>FULL</taxii_11:Response_Type>
        </taxii_11:Subscription_Parameters>
        <taxii_11:Push_Parameters>
            <taxii_11:Protocol_Binding>urn:taxii.mitre.org:protocol:https:1.0</taxii_11:Protocol_Binding>
            <taxii_11:Address>%(inbox_uri)s</taxii_11:Address>
            <taxii_11:Message_Binding>urn:taxii.mitre.org:message:xml:1.1</taxii_11:Message_Binding>
        </taxii_11:Push_Parameters>
        <taxii_11:Poll_Instance>
            <taxii_11:Protocol_Binding>urn:taxii.mitre.org:protocol:https:1.0</taxii_11:Protocol_Binding>
            <taxii_11:Address>%(poll_uri)s</taxii_11:Address>
            <taxii_11:Message_Binding>urn:taxii.mitre.org:message:xml:1.1</taxii_11:Message_Binding>
        </taxii_11:Poll_Instance>
    </taxii_11:Subscription>
</taxii_11:Subscription_Management_Response>
''' % dict(subscription_id=SUBSCRIPTION_ID, poll_uri=POLL_URI, inbox_uri=INBOX_URI, collection_name=POLL_COLLECTION)

INBOX_RESPONSE = '''
<taxii_11:Status_Message xmlns:taxii="http://taxii.mitre.org/messages/taxii_xml_binding-1" xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" xmlns:tdq="http://taxii.mitre.org/query/taxii_default_query-1" message_id="83710" in_response_to="57915" status_type="SUCCESS"/>
'''
