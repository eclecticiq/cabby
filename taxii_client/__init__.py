
from .client10 import Client10
from .client11 import Client11


def create_client(host, discovery_path=None, port=None, use_https=False, auth=None, version="1.1"):

    params = dict(port=port, use_https=use_https, auth=auth, discovery_path=discovery_path)

    if version == '1.1':
        return Client11(host, **params)
    elif version == '1.0':
        return Client10(host, **params)
    else:
        raise ValueError("TAXII version %s is not supported" % version)



