
from .client10 import Client10
from .client11 import Client11

def create_client(host, port=None, use_https=False, auth=dict(), version="1.1"):

    if version == '1.1':
        return Client11(host, port=port, use_https=use_https, auth=auth)
    elif version == '1.0':
        return Client10(host, port=port, use_https=use_https, auth=auth)
    else:
        raise ValueError("TAXII version %d is not supported" % version)
