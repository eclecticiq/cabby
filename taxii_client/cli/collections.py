#!/usr/bin/env python

from libtaxii.constants import SVC_COLLECTION_MANAGEMENT, SVC_FEED_MANAGEMENT

from .commons import run_client, get_basic_arg_parser


def _runner(client, path, args):

    services = client.discover_services(uri=path)

    collections = []

    for service in services:
        if hasattr(client, 'get_collections') and \
                service.service_type == SVC_COLLECTION_MANAGEMENT:

            collections.append(client.get_collections(uri=service.service_address))

        elif hasattr(client, 'get_feeds') and \
                service.service_type == SVC_FEED_MANAGEMENT:

            collections.append(client.get_feeds(uri=service.service_address))


    for c in collections:
        if args.as_xml:
            print c.to_xml(pretty_print=True)
        else:
            print c.to_text()


def fetch_collections():
    run_client(get_basic_arg_parser(), _runner)


