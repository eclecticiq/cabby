
import os
import re
import pytz
import logging
import hashlib
import dateutil.parser

from .commons import run_client, get_basic_arg_parser

log = logging.getLogger(__name__)


def extend_arguments(parser):
    parser.add_argument(
        "-c", "--collection", dest="collection",
        help="collection to poll", required=True)

    parser.add_argument(
        "--dest-dir", dest="dest_dir",
        help="directory to save polled content")

    parser.add_argument(
        "-l", "--limit", dest="limit", type=int,
        default=None,
        help="limit the number of content blocks returned")

    parser.add_argument(
        "-r", "--raw", dest="as_raw", action='store_true',
        help=("output raw TAXII messages "
              "(use in combination with -x to see them as XML)"))

    parser.add_argument(
        "--begin", dest="begin",
        help="exclusive beginning of time window as ISO8601 formatted date")

    parser.add_argument(
        "--end", dest="end",
        help="inclusive ending of time window as ISO8601 formatted date")

    parser.add_argument(
        "-b", "--bindings", dest="bindings",
        help=("Only return data for the listed content bindings, using "
              "a string with multiple items seperated by a ','. "
              "Defauls to all content."))

    parser.add_argument(
        "-s", "--subscription", dest="subscription_id",
        help="ID of an existing subscription")

    parser.add_argument(
        "--count-only", dest="count_only", action='store_true',
        help="retrieve only count of content blocks")

    return parser


def generate_filename(collection, content_block):

    collection_name = re.sub(r"[^\w]+", "-", collection) if collection else ""

    md5 = hashlib.md5()
    md5.update(content_block.raw.to_xml())

    filename = '%s_%s' % (collection_name, md5.hexdigest())

    return filename


def save_to_dir(dest_dir, collection, content_block, as_raw):

    filename = generate_filename(collection, content_block)
    path = os.path.abspath(os.path.join(dest_dir, filename))

    with open(path, 'wb') as f:
        if as_raw:
            content = content_block.raw.to_xml(pretty_print=True)
        else:
            content = content_block.content

        f.write(
            content if isinstance(content, bytes)
            else content.encode('utf-8'))

    log.info("Content block saved to %s", path)


def _runner(client, path, args):

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

    bindings = args.bindings.split(',') if args.bindings else None
    log.info("Polling using data binding: %s",
             str(bindings) if bindings else "ALL")

    if args.count_only:
        count = client.get_content_count(
            collection_name=args.collection,
            begin_date=begin,
            end_date=end,
            subscription_id=args.subscription_id,
            uri=path,
            content_bindings=bindings,
        )
        if count:
            log.info("Content blocks count: %s, is partial: %s",
                     count.count, count.is_partial)
        else:
            log.warning("Count value was not returned")

        return

    blocks = client.poll(
        collection_name=args.collection,
        begin_date=begin,
        end_date=end,
        subscription_id=args.subscription_id,
        uri=path,
        content_bindings=bindings,
    )

    counter = 0

    for counter, block in enumerate(blocks, 1):
        if args.dest_dir:
            dest_dir = os.path.abspath(args.dest_dir)
            save_to_dir(dest_dir, args.collection, block, args.as_raw)
        else:
            if args.as_raw:
                if args.as_xml:
                    value = block.raw.to_xml()
                else:
                    value = block.raw.to_text()
            else:
                value = block.content
            print(value.decode('utf-8'))

        if args.limit and counter >= args.limit:
            break

    log.info("%d blocks polled", counter)


def poll_content():
    run_client(extend_arguments(get_basic_arg_parser()), _runner)
