import argparse
import logging
import dateutil
import pytz

from cabby import create_client
from cabby.constants import (
    CB_STIX_XML_111, CB_CAP_11, CB_SMIME,
    CB_STIX_XML_10, CB_STIX_XML_101, CB_STIX_XML_11, CB_XENC_122002)

from .commons import (
    DEFAULT_VERSION, VERSION_CHOICES,
    configure_color_logging, prepare_headers
)

log = logging.getLogger(__name__)

# Extra Binding
CB_STIX_XML_12 = 'urn:stix.mitre.org:xml:1.2'
DEFAULT_BINDING = CB_STIX_XML_111
BINDING_CHOICES = [CB_STIX_XML_111, CB_CAP_11, CB_SMIME, CB_STIX_XML_12,
                   CB_STIX_XML_10, CB_STIX_XML_101, CB_STIX_XML_11,
                   CB_XENC_122002]


# Proxy will be:
#   source polling service  => destination inbox service
#   * Content binding is similar
#   * Message binding can be different
#   * collection is different

def service_arguments(parser, ident, descriptor):
    parser.add_argument(
        "--{}-path".format(ident), dest="{}_path".format(ident),
        help="Address of the {} service".format(descriptor),
        required=True)

    parser.add_argument(
        "--{}-collection".format(ident), dest="{}_collection".format(ident),
        help="The collection to {}".format(descriptor),
        required=True)

    parser.add_argument(
        "--{}-taxii-version".format(ident),
        dest="{}_taxii_version".format(ident),
        help="The TAXII version to use for {}".format(descriptor),
        default=DEFAULT_VERSION, choices=VERSION_CHOICES)

    parser.add_argument(
        "--{}-username".format(ident), dest="{}_username".format(ident),
        help="username for {} authentication".format(descriptor))

    parser.add_argument(
        "--{}-password".format(ident), dest="{}_password".format(ident),
        help="password for {} authentication".format(descriptor))

    parser.add_argument(
        "--{}-jwt-auth".format(ident), dest="{}_jwt_auth_url".format(ident),
        help="JWT authentication URL for {}".format(descriptor))

    parser.add_argument(
        "--{}-header".format(ident), dest="{}_headers".format(ident),
        action='append',
        help="header to send with the {} request, as header:value pair".format(
            descriptor))

    return parser


def common_arguments(parser):
    parser.add_argument(
        "-v", "--verbose", dest="verbose",
        action='store_true',
        help="verbose mode")

    parser.add_argument(
        "--binding", dest="binding",
        default=DEFAULT_BINDING, choices=BINDING_CHOICES,
        help="content binding")

    parser.add_argument(
        "-l", "--limit", dest="limit", type=int,
        default=None,
        help="limit the number of content blocks to push")

    parser.add_argument(
        "--begin", dest="begin",
        help="exclusive beginning of time window as ISO8601 formatted date")

    parser.add_argument(
        "--end", dest="end",
        help="inclusive ending of time window as ISO8601 formatted date")

    return parser


def get_blocks(client, args):
    if args.limit == 0:
        return

    if args.begin:
        begin = dateutil.parser.parse(args.begin)
        if not begin.tzinfo:
            begin = begin.replace(tzinfo=pytz.UTC)
    else:
        begin = None

    if args.end:
        end = dateutil.parser.parse(args.end)
        if not end.tzinfo:
            end = end.replace(tzinfo=pytz.UTC)
    else:
        end = None

    blocks = client.poll(
        collection_name=args.poll_collection,
        begin_date=begin,
        end_date=end,
        uri=args.poll_path,
        content_bindings=[args.binding],
    )

    counter = 0

    for counter, block in enumerate(blocks, 1):
        yield block.content.decode('utf-8')
        if args.limit and counter >= args.limit:
            break

    log.info("%d blocks polled", counter)


def _runner(poll, inbox, args):

    # Get stuff from poll
    blocks = get_blocks(poll, args)

    for block in blocks:
        log.debug("got block %s", block)
        inbox.push(
            block,
            args.binding,
            collection_names=[args.inbox_collection],
            uri=args.inbox_path)

    log.info("Content block successfully pushed")


def get_arg_parser():
    parser = argparse.ArgumentParser(
        description="TAXII Proxy Client",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Specific arguments
    parser = service_arguments(parser, 'inbox', 'inbox')
    parser = service_arguments(parser, 'poll', 'polling')

    # Common
    parser = common_arguments(parser)

    return parser


def run_client(parser, run_func):
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    configure_color_logging(level=level)

    poll_headers = (prepare_headers(args.poll_headers)
                    if args.poll_headers else None)

    inbox_headers = (prepare_headers(args.inbox_headers)
                     if args.inbox_headers else None)

    poll_client = create_client(version=args.poll_taxii_version,
                                headers=poll_headers)
    inbox_client = create_client(version=args.inbox_taxii_version,
                                 headers=inbox_headers)

    poll_client.set_auth(
        username=args.poll_username,
        password=args.poll_password,
        jwt_auth_url=args.poll_jwt_auth_url
    )

    inbox_client.set_auth(
        username=args.inbox_username,
        password=args.inbox_password,
        jwt_auth_url=args.inbox_jwt_auth_url
    )

    try:
        run_func(poll_client, inbox_client, args)
    except Exception as e:
        log.error(e, exc_info=args.verbose)


def proxy_content():
    run_client(get_arg_parser(), _runner)
