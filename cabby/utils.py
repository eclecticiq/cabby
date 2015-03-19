import pytz
from datetime import datetime
from libtaxii.clients import HttpClient
import libtaxii.messages_11 as tm11

from .entities import ContentBinding

def get_utc_now():
    return datetime.utcnow().replace(tzinfo=pytz.UTC)


def configure_client_auth(tclient, cert_file=None, key_file=None,
        username=None, password=None):

    tls_auth = (cert_file and key_file)
    basic_auth = (username and password)

    if tls_auth and basic_auth:
        tclient.set_auth_type(HttpClient.AUTH_CERT_BASIC)
        tclient.set_auth_credentials(dict(
            key_file = key_file, 
            cert_file = cert_file,
            username = username,
            password = password
        ))
    elif tls_auth:
        tclient.set_auth_type(HttpClient.AUTH_CERT)
        tclient.set_auth_credentials(dict(
            key_file = key_file, 
            cert_file = cert_file,
        ))
    elif basic_auth:
        tclient.set_auth_type(HttpClient.AUTH_BASIC)
        tclient.set_auth_credentials(dict(
            username = username,
            password = password
        ))

    return tclient


def pack_content_bindings(content_bindings, version):

    if not content_bindings:
        return None

    bindings = []

    for b in content_bindings:
        if isinstance(b, ContentBinding):
            binding = tm11.ContentBinding(binding_id=b.id,
                    subtype_ids=b.subtypes) if version == 11 else b.id
        else:
            binding = tm11.ContentBinding(binding_id=b) \
                    if version == 11 else b

        bindings.append(binding)

    return bindings

