

class ClientException(Exception):
    pass


class UnsuccessfulStatusError(ClientException):

    def __init__(self, taxii_status, *args, **kwargs):
        super(UnsuccessfulStatusError, self).__init__(status_to_message(taxii_status), *args, **kwargs)

        self.status = taxii_status.status_type
        self.text = taxii_status.to_text()

        self.raw = taxii_status


class AmbiguousServicesError(ClientException):
    pass


class ServiceNotFoundError(ClientException):
    pass


class NoURIProvidedError(ValueError):
    pass


def status_to_message(status):
    message = status.status_type

    if status.status_detail:
        message += '; %s;' % dict_to_pairs(status.status_detail)

    if status.extended_headers:
        message += '; %s;' % dict_to_pairs(status.extended_headers)

    if status.message:
        message += '; message=%s' % status.message

    return message

def dict_to_pairs(d):
    pairs = []
    for k, v in d.items():
        pairs.append('%s=%s' % (k, v))
    return ", ".join(pairs)
