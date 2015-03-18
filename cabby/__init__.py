
from .client10 import Client10
from .client11 import Client11


def create_client(host=None, discovery_path=None, port=None, use_https=False,
        version="1.1"):

    params = dict(host=host, port=port, use_https=use_https,
            discovery_path=discovery_path)

    if version == '1.1':
        return Client11(**params)
    elif version == '1.0':
        return Client10(**params)
    else:
        raise ValueError("TAXII version %s is not supported" % version)

