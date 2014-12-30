
import pytz
import json
import calendar

from libtaxii.clients import HttpClient
from libtaxii.messages_10 import ContentBlock as ContentBlock10
from datetime import datetime

from collections import namedtuple


def ts_to_date(timestamp):

    if not timestamp:
        return None

    return datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.UTC)


def date_to_ts(obj):
    if obj.utcoffset() is not None:
        obj = obj - obj.utcoffset()

    millis = int(
        calendar.timegm(obj.timetuple()) * 1000 +
        obj.microsecond / 1000
    )
    return millis


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

    def default(self, obj):

        if isinstance(obj, datetime):
            return date_to_ts(obj)
        else:
            return JSONEncoder.default(self, obj)


AbstractContentBlock = namedtuple('AbstractContentBlock', ['content', 'binding', 'subtypes', 'timestamp', 'source', 'sink_collection', 'source_collection'])

class ContentBlock(AbstractContentBlock):

    def to_json(self):
        return json.dumps(self._asdict(), cls=DatetimeJSONEncoder)


def extract_content(response, source=None, source_collection=None, sink_collection=None):
    for block in response.content_blocks:
        if isinstance(block, ContentBlock10):
            yield ContentBlock(
                content = block.content,
                binding = block.content_binding,
                timestamp = block.timestamp_label,
                subtypes = [],
                source = source,
                source_collection = source_collection,
                sink_collection = sink_collection
            )
        else:
            yield ContentBlock(
                content = block.content,
                binding = block.content_binding.binding_id,
                timestamp = block.timestamp_label,
                subtypes = block.content_binding.subtype_ids,
                source = source,
                source_collection = source_collection,
                sink_collection = sink_collection
            )
