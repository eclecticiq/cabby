
import sys
import argparse
import logging

from taxii_client import create_client

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
    parser.add_argument("--path", dest="path", help="path to a TAXII Service")

    parser.add_argument("--https", dest="https", action='store_true', help="if the client should use HTTPS")

    parser.add_argument("--cert", dest="cert", help="certificate file")
    parser.add_argument("--key", dest="key", help="private key file")
    parser.add_argument("--username", dest="username", help="username for authentication")
    parser.add_argument("--password", dest="password", help="password for authentication")

    parser.add_argument("-v", "--verbose", dest="verbose", action='store_true', help="Verbose mode")
    parser.add_argument("-x", "--as-xml", dest="as_xml", action='store_true', help="Print response as raw XML")

    parser.add_argument("--taxii-version", dest="version", default=DEFAULT_VERSION, help="TAXII version to use")

    return parser


def _configure_logger(verbose):
    if verbose:
        configure_color_logging('', level=logging.DEBUG)
    else:
        configure_color_logging('', level=logging.INFO)

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

    try:
        run_func(client, args.path, args)
    except Exception, e:
        log.error(e.message, exc_info=args.verbose)


def configure_color_logging(logger_name, level):

    log = logging.getLogger(logger_name)

    log.setLevel(level)

    if level == logging.DEBUG:
        format_string = "%(asctime)s %(name)s %(log_color)s%(levelname)s:%(reset)s %(white)s%(message)s"
    else:
        format_string = "%(asctime)s %(log_color)s%(levelname)s:%(reset)s %(white)s%(message)s"

    from colorlog import ColoredFormatter

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
    log.addHandler(handlers)
    return log

