

class ClientException(Exception):
    pass


class UnsuccessfulStatusError(ClientException):

    def __init__(self, taxii_status, *args, **kwargs):
        super(UnsuccessfulStatusError, self).__init__('%s:\n%s' % (taxii_status.status_type, taxii_status.message), *args, **kwargs)

        self.status = taxii_status.status_type
        self.text = taxii_status.to_text()

        self.raw = taxii_status


class AmbiguousServicesError(ClientException):
    pass


class ServiceNotFoundError(ClientException):
    pass


class IllegalArgumentError(ValueError):
    pass
