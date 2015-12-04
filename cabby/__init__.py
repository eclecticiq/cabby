'''
    Cabby, python library for interacting with TAXII servers.
'''

from ._version import __version__  # noqa: used in setup.py

from .client10 import Client10
from .client11 import Client11


def create_client(host=None, port=None, discovery_path=None, use_https=False,
                  version="1.1", headers=None):
    '''Create a client instance (TAXII version specific).

    ``host``, ``port``, ``use_https``, ``discovery_path`` values
    can be overridden per request with ``uri`` argument passed to
    a client's method.

    :param str host: TAXII server hostname
    :param int port: TAXII server port
    :param str discovery_path: Discovery Service relative path
    :param bool use_https: if HTTPS should be used
    :param string version: TAXII version (1.1 or 1.0)
    :param dict headers: additional headers to pass with TAXII messages

    :return: client instance
    :rtype: :py:class:`cabby.client11.Client11` or
            :py:class:`cabby.client10.Client10`
    '''

    params = dict(
        host=host,
        port=port,
        use_https=use_https,
        discovery_path=discovery_path,
        headers=headers)

    if version == '1.1':
        return Client11(**params)
    elif version == '1.0':
        return Client10(**params)
    else:
        raise ValueError("TAXII version %s is not supported" % version)
