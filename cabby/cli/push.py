
import logging
import mimetypes

from cabby.entities import ContentBinding
from cabby.constants import CB_STIX_XML_111

from .commons import run_client, get_basic_arg_parser

log = logging.getLogger(__name__)

DEFAULT_BINDING = CB_STIX_XML_111


def extend_arguments(parser):

    parser.add_argument(
        "-f", "--content-file", dest="content_file",
        help="file with the content to send",
        required=True)

    parser.add_argument(
        "--binding", dest="binding",
        default=DEFAULT_BINDING,
        help="content binding")

    parser.add_argument(
        "--subtype", dest="subtypes",
        action='append',
        help="the subtype of the content binding")

    parser.add_argument(
        "--dest", dest="collections",
        action='append',
        help="names of the destination collections")

    return parser


def _runner(client, path, args):

    content_file_path = args.content_file
    content_file_type = mimetypes.guess_type(content_file_path)

    readability = None

    if content_file_type[0][:4] == "text" or \
        (content_file_type[0] == None and content_file_type[1] == None):
        readability = 'r'
    else:
        readability = 'rb'

    with open(content_file_path, readability) as f:
        content = f.read()

    if args.binding and args.subtypes:
        binding = ContentBinding(args.binding, subtypes=args.subtypes)
    elif args.binding:
        binding = args.binding
    else:
        binding = None

    client.push(content, binding, collection_names=args.collections, uri=path)

    log.info("Content block successfully pushed")


def push_content():
    run_client(extend_arguments(get_basic_arg_parser()), _runner)
