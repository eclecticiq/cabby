
import sys
import argparse

from taxii_client import create_client

import logging
log = logging.getLogger(__name__)

DEFAULT_PORT = 80
DEFAULT_VERSION = '1.1'

def get_basic_arg_parser():

    parser = argparse.ArgumentParser(
        description = "TAXII client",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--host", help="host where the TAXII Service is hosted", required=True)
    parser.add_argument("--port", dest="port", default=DEFAULT_PORT, type=int, help="port where the TAXII Service is hosted")
    parser.add_argument("--discovery", dest="discovery", help="path to a TAXII Discovery service")
    parser.add_argument("--path", dest="path", help="path to a TAXII Service")

    parser.add_argument("--https", dest="https", action='store_true', help="if the client should use HTTPS")

    parser.add_argument("--cert", dest="cert", help="certificate file")
    parser.add_argument("--key", dest="key", help="private key file")
    parser.add_argument("--username", dest="username", help="username for authentication")
    parser.add_argument("--password", dest="password", help="password for authentication")

    parser.add_argument("-v", "--verbose", dest="verbose", action='store_true', help="Verbose mode")

    parser.add_argument("--taxii-version", dest="version", default=DEFAULT_VERSION, help="TAXII version to use")

    return parser


def _configure_logger(verbose):
    if verbose:
        logger_format = '%(asctime)s %(name)s %(levelname)s: %(message)s'
        logging.basicConfig(level=logging.DEBUG, format=logger_format)
    else:
        logger_format = '%(asctime)s %(levelname)s: %(message)s'
        logging.basicConfig(level=logging.INFO, format=logger_format)

def is_args_valid(args):

    if not args.path and not args.discovery:
        log.error("Either --path or --discovery need to be specified")
        return False

    return True
        

def run_client(extend_arguments_func, run_func):

    parser = extend_arguments_func(get_basic_arg_parser())
    args = parser.parse_args()

    _configure_logger(args.verbose)

    if not is_args_valid(args):
        sys.exit(1)


    auth_details = dict(
        cert = args.cert,
        key = args.key,
        username = args.username,
        password = args.password
    )

    client = create_client(args.host, discovery_path=args.discovery, port=args.port,
            use_https=args.https, auth=auth_details, version=args.version)

    run_func(client, args.path, args)

