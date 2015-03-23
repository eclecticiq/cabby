from libtaxii.constants import SVC_COLLECTION_MANAGEMENT, SVC_FEED_MANAGEMENT

from .commons import run_client, get_basic_arg_parser

def _get_collections(client, path):

    if hasattr(client, 'get_collections'):
        return client.get_collections(uri=path)
    elif hasattr(client, 'get_feeds'):
        return client.get_feeds(uri=path)


def _runner(client, path, args):

    collections = []

    if path:
        collections.extend(_get_collections(client, path))
    else:
        for service in client.get_services(service_types=[SVC_COLLECTION_MANAGEMENT, SVC_FEED_MANAGEMENT]):
            _collections = _get_collections(client, service.service_address)
            collections.extend(_collections)

    for c in collections:
        if args.as_xml:
            print c.raw.to_xml(pretty_print=True)
        else:
            print c.raw.to_text()


def fetch_collections():
    run_client(get_basic_arg_parser(), _runner)


