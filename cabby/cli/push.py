import logging

from libtaxii.constants import CB_STIX_XML_111

from .commons import run_client, get_basic_arg_parser

log = logging.getLogger(__name__)

DEFAULT_BINDING = CB_STIX_XML_111

def extend_arguments(parser):
    parser.add_argument("-f", "--content-file", dest="content_file", help="file with the content to send", required=True)
    parser.add_argument("--binding", dest="content_binding", default=DEFAULT_BINDING, help="content binding")
    parser.add_argument("--subtype", dest="subtype", help="the subtype of the content binding")
    parser.add_argument("--dest", dest="collections", action='append', help="names of the destination collections")

    return parser


def _runner(client, path, args):

    with open(args.content_file, 'r') as f:
        content = f.read()

    client.push(content, args.content_binding, subtype=args.subtype,
            collections_names=args.collections, uri=path)

    log.info("Content pushed into %s", path)


def push_content():
    run_client(extend_arguments(get_basic_arg_parser()), _runner)

