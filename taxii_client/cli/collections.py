#!/usr/bin/env python

from libtaxii.constants import SVC_COLLECTION_MANAGEMENT, SVC_FEED_MANAGEMENT

from .commons import run_client, get_basic_arg_parser


COLLECTION_SERVICES = [SVC_COLLECTION_MANAGEMENT, SVC_FEED_MANAGEMENT]


def _runner(client, path, args):

    services = client.discover_services(uri=path)

    collections = []

    for service in services:
        if service.service_type in COLLECTION_SERVICES:
            fetched = client.get_collections(uri=service.service_address)
            collections.append(fetched)


    for c in collections:
        if args.as_xml:
            print c.to_xml(pretty_print=True)
        else:
            print c.to_text()


def fetch_collections():
    run_client(get_basic_arg_parser(), _runner)


