
import pytz

from libtaxii.clients import HttpClient
from datetime import datetime


def ts_to_date(timestamp):

    if not timestamp:
        return None

    date = datetime.utcfromtimestamp(timestamp)
    date = date.replace(tzinfo=pytz.UTC)

    return date


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


def extract_content(response):
    for block in response.content_blocks:
        yield dict(
            content = block.content,
            binding = (block.content_binding.binding_id, block.content_binding.subtype_ids),

            timestamp = block.timestamp_label,

            is_xml = block.content_is_xml
        )
