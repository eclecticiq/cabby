
import logging
import sys
import argparse
from colorlog import ColoredFormatter

from .. import create_client

log = logging.getLogger(__name__)

DEFAULT_VERSION = '1.1'

def get_basic_arg_parser():

    parser = argparse.ArgumentParser(
        description = "TAXII client",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--host", help="host where the TAXII Service is hosted", required=True)
    parser.add_argument("--port", dest="port", type=int, help="port where the TAXII Service is hosted")
    parser.add_argument("--discovery", dest="discovery", help="path to a TAXII Discovery service")
    parser.add_argument("--path", dest="path", help="path to a specific TAXII Service")

    parser.add_argument("--https", dest="https", action='store_true', help="if the client should use HTTPS")

    parser.add_argument("--cert", dest="cert", help="certificate file")
    parser.add_argument("--key", dest="key", help="private key file")
    parser.add_argument("--username", dest="username", help="username for authentication")
    parser.add_argument("--password", dest="password", help="password for authentication")

    parser.add_argument("-v", "--verbose", dest="verbose", action='store_true', help="Verbose mode")
    parser.add_argument("-x", "--as-xml", dest="as_xml", action='store_true', help="Print response as raw XML")

    parser.add_argument("--taxii-version", dest="version", default=DEFAULT_VERSION, help="TAXII version to use")

    return parser



def is_args_valid(args):

    if not args.path and not args.discovery:
        log.error("Either --path or --discovery need to be specified")
        return False

    return True
        

def run_client(parser, run_func):

    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    configure_color_logging(level=level)

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

    try:
        run_func(client, args.path, args)
    except Exception, e:
        log.error(e.message, exc_info=args.verbose)


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

