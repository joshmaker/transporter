from urlparse import urlparse
import os
import adapters
try:
    import paramiko
except ImportError:
    pass


"""The following protocals are supported ftp, ftps, http and https.
sftp and ssh require paramiko to be installed
"""


class Transporter(object):

    availible_adapters = {
        "ftp": adapters.FtpAdapter,
        "ftps": adapters.FtpAdapter,
        "file": adapters.LocalFileAdapter,
        "http": adapters.HttpAdapter,
        "https": adapters.HttpAdapter,
    }
    default_scheme = "file"
    adapter = None

    def __init__(self, uri):
        uri = urlparse(uri)
        scheme = uri.scheme or self.default_scheme
        if scheme not in self.availible_adapters:
            msg = u"{0} is not a support scheme. Availible schemes: {1}".format(
                    scheme, [s for s in self.availible_adapters])
            raise NotImplemented(msg)

        self.adapter = self.availible_adapters[scheme](uri)

    def __getattr__(self, attr):
        return getattr(self.adapter, attr)

    def __repr__(self):
        return u'<Transporter {0}>'.format(self.adapter.__repr__())


def get(uri):
    f = os.path.basename(uri)
    uri = os.path.dirname(uri)
    return Transporter(uri).get(f)


def put(uri, data):
    f = os.path.basename(uri)
    uri = os.path.dirname(uri)
    return Transporter(uri).put(f, data)


def transport(source, destination):
    return put(destination, get(source))
