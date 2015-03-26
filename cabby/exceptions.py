

class ClientException(Exception):
    pass

class HTTPError(ClientException):
    pass

class UnsuccessfulStatusError(ClientException):

    def __init__(self, taxii_status, *args, **kwargs):
        super(UnsuccessfulStatusError, self).__init__(_status_to_message(taxii_status), *args, **kwargs)

        self.status = taxii_status.status_type
        self.text = taxii_status.to_text()

        self.raw = taxii_status


class AmbiguousServicesError(ClientException):
    pass


class ServiceNotFoundError(ClientException):
    pass


class NoURIProvidedError(ValueError):
    pass


def _status_to_message(status):
    l = [status.status_type]

    if status.status_detail:
        l.append(_dict_to_pairs(status.status_detail))

    if status.extended_headers:
        l.append(_dict_to_pairs(status.extended_headers))
    
    if status.message:
        l.append(status.message)

    return "; ".join(l)


def _dict_to_pairs(d):
    pairs = []
    for k, v in d.items():
        pairs.append('%s=%s' % (k, v))
    return ", ".join(pairs)
