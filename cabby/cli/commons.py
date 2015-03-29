import logging
import sys
import argparse
from colorlog import ColoredFormatter

from ..abstract import AbstractClient
from .. import create_client

log = logging.getLogger(__name__)

TAXII_10 = '1.0'
TAXII_11 = '1.1'
DEFAULT_VERSION = TAXII_11

VERSION_CHOICES = [TAXII_10, TAXII_11]

def get_basic_arg_parser():

    parser = argparse.ArgumentParser(
        description = "TAXII client",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--host", dest="host", help="host where the TAXII Service is hosted")
    parser.add_argument("--port", dest="port", type=int, help="port where the TAXII Service is hosted")
    parser.add_argument("--discovery", dest="discovery", help="path to a TAXII Discovery service")
    parser.add_argument("--path", dest="uri", help="absolute path (as URL) or relative path to a specific TAXII Service")

    parser.add_argument("--https", dest="https", action='store_true', help="if the client should use HTTPS")

    parser.add_argument("--cert", dest="cert", help="certificate file")
    parser.add_argument("--key", dest="key", help="private key file")
    parser.add_argument("--username", dest="username", help="username for authentication")
    parser.add_argument("--password", dest="password", help="password for authentication")

    parser.add_argument("--proxy-url", dest="proxy_url", help="proxy address formatted as URL. Can be set to 'noproxy' to force library to not use any proxy")
    parser.add_argument("--proxy-type", dest="proxy_type", choices=AbstractClient.PROXY_TYPE_CHOICES, help="proxy type")

    parser.add_argument("--header", dest="headers", action='append', help="header to send with the request, as header:value pair")

    parser.add_argument("-v", "--verbose", dest="verbose", action='store_true', help="verbose mode")
    parser.add_argument("-x", "--as-xml", dest="as_xml", action='store_true', help="output raw XML")

    parser.add_argument("-t", "--taxii-version", dest="version", default=DEFAULT_VERSION, choices=VERSION_CHOICES, help="TAXII version to use")

    return parser



def is_args_valid(args):

    if not args.uri and not args.discovery:
        log.error("Either 'discovery' or 'path' needs to be specified")
        return False

    return True
        

def prepare_headers(raw_headers):
    headers = {}

    for line in raw_headers:
        header, value = line.split(":", 1)
        headers[header] = value.strip('"\'')

    return headers


def run_client(parser, run_func):

    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    configure_color_logging(level=level)

    if not is_args_valid(args):
        sys.exit(1)

    headers = prepare_headers(args.headers) if args.headers else None

    client = create_client(host=args.host, discovery_path=args.discovery, port=args.port,
            use_https=args.https, version=args.version, headers=headers)

    client.set_auth(
        cert_file = args.cert,
        key_file = args.key,
        username = args.username,
        password = args.password
    )

    if args.proxy_url:
        client.set_proxy(args.proxy_url, proxy_type=args.proxy_type)

    try:
        run_func(client, args.uri, args)
    except Exception, e:
        log.error(e, exc_info=args.verbose)


def configure_color_logging(level, logger_name=None):

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    if level == logging.DEBUG:
        format_string = "%(asctime)s %(name)s %(log_color)s%(levelname)s:%(reset)s %(white)s%(message)s"
    else:
        format_string = "%(asctime)s %(log_color)s%(levelname)s:%(reset)s %(white)s%(message)s"

    formatter = ColoredFormatter(
        format_string,
        datefmt = None,
        reset = True,
        log_colors = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }
    )

    handlers = logging.StreamHandler(sys.stderr)
    handlers.setFormatter(formatter)
    logger.addHandler(handlers)

