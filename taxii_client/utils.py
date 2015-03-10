
import calendar
import pytz
import json

from datetime import datetime

from libtaxii.clients import HttpClient

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




