from libtaxii import messages_11 as tm11
from libtaxii import messages_10 as tm10

STREAM_MARKER = 'STREAM'

TAXII_11_NS = 'http://taxii.mitre.org/messages/taxii_xml_binding-1.1'
TAXII_10_NS = 'http://taxii.mitre.org/messages/taxii_xml_binding-1'

XML_11_BINDING = 'urn:taxii.mitre.org:message:xml:1.1'
XML_10_BINDING = 'urn:taxii.mitre.org:message:xml:1.0'
CERT_EU_JSON_10_BINDING = 'urn:cert.europa.eu:message:json:1.0'

VERSIONS = {
    TAXII_11_NS: XML_11_BINDING,
    TAXII_10_NS: XML_10_BINDING
}

MODULES = {
    TAXII_11_NS: tm11,
    TAXII_10_NS: tm10
}

SUPPORTED_CONTENT_BINDINGS = [
    XML_11_BINDING, XML_10_BINDING, CERT_EU_JSON_10_BINDING]

BINDINGS_TO_CONTENT_TYPE = {
    XML_11_BINDING: 'application/xml',
    XML_10_BINDING: 'application/xml',
    CERT_EU_JSON_10_BINDING: 'application/json'
}

TAXII_SERVICES_10 = 'urn:taxii.mitre.org:services:1.0'
TAXII_SERVICES_11 = 'urn:taxii.mitre.org:services:1.1'

BINDINGS_TO_SERVICES = {
    XML_10_BINDING: TAXII_SERVICES_10,
    XML_11_BINDING: TAXII_SERVICES_11,
    CERT_EU_JSON_10_BINDING: 'urn:taxii.mitre.org:services:1.0'
}

PROTOCOL_HTTP_10_BINDING = 'urn:taxii.mitre.org:protocol:http:1.0'
PROTOCOL_HTTPS_10_BINDING = 'urn:taxii.mitre.org:protocol:https:1.0'

SCHEMA_TO_PROTOCOL_BINDINGS = {
    'https': PROTOCOL_HTTPS_10_BINDING,
    'http': PROTOCOL_HTTP_10_BINDING
}

# Constant identifying a Status Message
MSG_STATUS_MESSAGE = 'Status_Message'
# Constant identifying a Discovery Request Message
MSG_DISCOVERY_REQUEST = 'Discovery_Request'
# Constant identifying a Discovery Response Message
MSG_DISCOVERY_RESPONSE = 'Discovery_Response'
# Constant identifying a Feed Information Request Message
MSG_FEED_INFORMATION_REQUEST = 'Feed_Information_Request'
# Constant identifying a Feed Information Response Message
MSG_FEED_INFORMATION_RESPONSE = 'Feed_Information_Response'
# Constant identifying a Subscription Management Request Message
MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST = 'Subscription_Management_Request'
# Constant identifying a Subscription Management Response Message
MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE = 'Subscription_Management_Response'
# Constant identifying a Poll Request Message
MSG_POLL_REQUEST = 'Poll_Request'
# Constant identifying a Poll Response Message
MSG_POLL_RESPONSE = 'Poll_Response'
# Constant identifying a Inbox Message
MSG_INBOX_MESSAGE = 'Inbox_Message'

# New Message Types in TAXII 1.1

# Constant identifying a Status Message
MSG_POLL_FULFILLMENT_REQUEST = 'Poll_Fulfillment'
# Constant identifying a Collection Information Request
MSG_COLLECTION_INFORMATION_REQUEST = 'Collection_Information_Request'
# Constant identifying a Collection Information Response
MSG_COLLECTION_INFORMATION_RESPONSE = 'Collection_Information_Response'
# Constant identifying a Subscription Request
MSG_MANAGE_COLLECTION_SUBSCRIPTION_REQUEST = 'Subscription_Management_Request'
# Constant identifying a Subscription Response
MSG_MANAGE_COLLECTION_SUBSCRIPTION_RESPONSE = \
    'Subscription_Management_Response'


# Constant identifying a Service Type of Inbox
SVC_INBOX = 'INBOX'
# Constant identifying a Service Type of Poll
SVC_POLL = 'POLL'
# Constant identifying a Service Type of Feed Management
SVC_FEED_MANAGEMENT = 'FEED_MANAGEMENT'
# Constant identifying a Service Type of Discovery
SVC_DISCOVERY = 'DISCOVERY'

# Tuple of all TAXII 1.0 Service Types
SVC_TYPES_10 = (SVC_INBOX, SVC_POLL, SVC_FEED_MANAGEMENT, SVC_DISCOVERY)

# Renamed Status Types in TAXII 1.1
# Constant identifying a Service Type of Collection Management.
# "Feed Management" was renamed to "Collection Management" in TAXII 1.1.
SVC_COLLECTION_MANAGEMENT = 'COLLECTION_MANAGEMENT'


SVC_TYPES = [
    SVC_INBOX, SVC_POLL, SVC_COLLECTION_MANAGEMENT, SVC_DISCOVERY,
    SVC_FEED_MANAGEMENT]

# TAXII 1.0 Action Types

# Constant identifying an Action of Subscribe
ACT_SUBSCRIBE = 'SUBSCRIBE'
# Constant identifying an Action of Unsubscribe
ACT_UNSUBSCRIBE = 'UNSUBSCRIBE'
# Constant identifying an Action of Status
ACT_STATUS = 'STATUS'

# Tuple of all TAXII 1.0 Action Types
ACT_TYPES_10 = (ACT_SUBSCRIBE, ACT_UNSUBSCRIBE, ACT_STATUS)

# Constant identifying an Action of Pause
ACT_PAUSE = 'PAUSE'
# Constant identifying an Action of Resume
ACT_RESUME = 'RESUME'

# Subscription Status of Active
SS_ACTIVE = 'ACTIVE'
# Subscription Status of Paused
SS_PAUSED = 'PAUSED'
# Subscription Status of Unsubscribed
SS_UNSUBSCRIBED = 'UNSUBSCRIBED'


# Constant identifying a response type of Full
RT_FULL = 'FULL'
# Constant identifying a response type of Count only
RT_COUNT_ONLY = 'COUNT_ONLY'

# Constant identifying a collection type of Data Feed
CT_DATA_FEED = 'DATA_FEED'
# Constant identifying a collection type of Data Set
CT_DATA_SET = 'DATA_SET'

# Content Binding ID for STIX XML 1.0
CB_STIX_XML_10 = 'urn:stix.mitre.org:xml:1.0'
# Content Binding ID for STIX XML 1.0.1
CB_STIX_XML_101 = 'urn:stix.mitre.org:xml:1.0.1'
# Content Binding ID for STIX XML 1.1
CB_STIX_XML_11 = 'urn:stix.mitre.org:xml:1.1'
# Content Binding ID for STIX XML 1.1.1
CB_STIX_XML_111 = 'urn:stix.mitre.org:xml:1.1.1'
# Content Binding ID for CAP 1.1
CB_CAP_11 = 'urn:oasis:names:tc:emergency:cap:1.1'
# Content Binding ID for XML Encryption
CB_XENC_122002 = 'http://www.w3.org/2001/04/xmlenc#'
# Content Binding ID for SMIME
CB_SMIME = 'application/x-pks7-mime'
