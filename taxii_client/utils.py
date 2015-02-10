
import calendar
import pytz
import json

from libtaxii.clients import HttpClient
from libtaxii.messages_10 import ContentBlock as ContentBlock10

from collections import namedtuple


def configure_taxii_client_auth(tclient, cert=None, key=None, username=None, password=None):
    tls_auth = (cert and key)
    basic_auth = (username and password)

    if tls_auth and basic_auth:
        tclient.set_auth_type(HttpClient.AUTH_CERT_BASIC)
        tclient.set_auth_credentials(dict(
            key_file = key, 
            cert_file = cert,
            username = username,
            password = password
        ))
    elif tls_auth:
        tclient.set_auth_type(HttpClient.AUTH_CERT)
        tclient.set_auth_credentials(dict(
            key_file = key, 
            cert_file = cert
        ))
    elif basic_auth:
        tclient.set_auth_type(HttpClient.AUTH_BASIC)
        tclient.set_auth_credentials(dict(
            username = username,
            password = password
        ))

    return tclient


class DatetimeJSONEncoder(json.JSONEncoder):
    '''Datetime aware JSON encoder'''

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)




class ContentBlock(namedtuple('AbstractContentBlock', ['content', 'binding', 'subtypes',
    'timestamp', 'source', 'sink_collection', 'source_collection'])):

    def to_json(self):
        return json.dumps(self._asdict(), cls=DatetimeJSONEncoder)


def extract_content(block, source=None, source_collection=None, sink_collection=None):

    if isinstance(block, ContentBlock10):
        binding = block.content_binding
        subtypes = None
    else:
        binding = block.content_binding.binding_id
        subtypes = block.content_binding.subtype_ids

    return ContentBlock(
        binding = binding,
        content = block.content,
        timestamp = block.timestamp_label,
        subtypes = subtypes,
        source = source,
        source_collection = source_collection,
        sink_collection = sink_collection
    )
