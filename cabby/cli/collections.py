

from cabby.constants import (
    SVC_COLLECTION_MANAGEMENT, SVC_FEED_MANAGEMENT)

from .commons import run_client, get_basic_arg_parser


def _runner(client, path, args):

    collections = []

    if path:
        collections.extend(client.get_collections(uri=path))
    else:
        service_types = [SVC_COLLECTION_MANAGEMENT, SVC_FEED_MANAGEMENT]
        for service in client.get_services(service_types=service_types):
            collections.extend(
                client.get_collections(uri=service.address))

    for c in collections:
        if args.as_xml:
            print(c.raw.to_xml(pretty_print=True))
        else:
            print(c.raw.to_text())


def fetch_collections():
    run_client(get_basic_arg_parser(), _runner)
