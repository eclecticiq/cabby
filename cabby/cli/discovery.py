
from .commons import run_client, get_basic_arg_parser


def _runner(client, path, args):

    services = client.discover_services(uri=path)

    for s in services:
        if args.as_xml:
            print(s.raw.to_xml(pretty_print=True).decode('utf-8'))
        else:
            print(s.raw.to_text())


def discover_services():
    run_client(get_basic_arg_parser(), _runner)
