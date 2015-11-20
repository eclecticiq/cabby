

class ClientException(Exception):
    pass


class HTTPError(ClientException):

    def __init__(self, status_code):
        super(ClientException, self).__init__(
            'HTTP Error: status code {}'.format(status_code))


class InvalidResponseError(ClientException):
    pass


class UnsuccessfulStatusError(ClientException):

    def __init__(self, taxii_status, *args, **kwargs):
        super(UnsuccessfulStatusError, self).__init__(
            _status_to_message(taxii_status), *args, **kwargs)

        self.status = taxii_status.status_type
        self.text = taxii_status.to_text()

        self.raw = taxii_status


class AmbiguousServicesError(ClientException):
    pass


class ServiceNotFoundError(ClientException):
    pass


class NoURIProvidedError(ValueError):
    pass


class NotSupportedError(ClientException):

    def __init__(self, version, *args, **kwargs):
        super(NotSupportedError, self).__init__(
            "Not supported in version {}".format(version),
            *args, **kwargs)


def _status_to_message(status):
    details = []

    if status.status_detail:
        details.append(_dict_to_pairs(status.status_detail))

    if status.extended_headers:
        details.append(_dict_to_pairs(status.extended_headers))

    if status.message:
        details.append(status.message)

    return "{}: {}".format(status.status_type, "; ".join(details))


def _dict_to_pairs(d):
    pairs = []
    for k, v in list(d.items()):
        pairs.append('%s=%s' % (k, v))
    return ", ".join(pairs)
