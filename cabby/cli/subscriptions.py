from .commons import run_client, get_basic_arg_parser, TAXII_10

ACTIONS = ['subscribe', 'status', 'pause', 'resume', 'unsubscribe']
REQUIRED_SID = ['unsubscribe', 'pause', 'resume']
ONLY_TAXII_11 = ['pause', 'resume']


def extend_arguments(parser):

    parser.add_argument(
        "-a", "--action", dest="action", choices=ACTIONS,
        help="action to perform", required=True)

    parser.add_argument(
        "-c", "--collection", dest="collection_name",
        help="collection name fo subscription", required=True)

    parser.add_argument(
        "-s", "--subscription", dest="subscription_id",
        help="ID of an existing subscription")

    parser.add_argument(
        "--count-only", dest="count_only", action='store_true',
        help="if subscribing only for content counts")

    return parser


def _runner(client, uri, args):

    if not args.subscription_id and args.action in REQUIRED_SID:
        raise ValueError("Action '%s' requires subscription ID" % args.action)

    if args.action in ONLY_TAXII_11 and args.version == TAXII_10:
        raise ValueError('Action "{}" is not supported in TAXII v{}'.format(
                         args.action, args.version))

    if args.action == 'subscribe':
        response = client.subscribe(
            args.collection_name,
            count_only=args.count_only,
            uri=uri)

    elif args.action == 'status':
        response = client.get_subscription_status(
            args.collection_name,
            subscription_id=args.subscription_id,
            uri=uri)

    elif args.action == 'pause':
        response = client.pause_subscription(
            args.collection_name,
            args.subscription_id,
            uri=uri)

    elif args.action == 'resume':
        response = client.resume_subscription(
            args.collection_name,
            args.subscription_id,
            uri=uri)

    elif args.action == 'unsubscribe':
        response = client.unsubscribe(
            args.collection_name,
            args.subscription_id,
            uri=uri)

    if args.as_xml:
        print(response.raw.to_xml(pretty_print=True))
    else:
        print(response.raw.to_text())


def manage_subscription():
    run_client(extend_arguments(get_basic_arg_parser()), _runner)
