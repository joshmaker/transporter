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
        "file": adapters.LocalFileAdapter
    }
    adapter = None

    def __init__(self, uri):
        uri = urlparse(uri)
        if uri.scheme not in self.availible_adapters:
            msg = u"{0} is not a support scheme. Availible schemes: {1}".format(
                    uri.scheme, [s for s in self.availible_adapters])
            raise NotImplemented(msg)

        self.adapter = self.availible_adapters[uri.scheme](uri)

    def __getattr__(self, attr):
        return getattr(self.adapter, attr)

    def __repr__(self):
        return u'<Transporter {0}>'.format(self.adapter.__repr__())


def download(uri):
    f = os.path.basename(uri)
    uri = os.path.dirname(uri)
    uri = urlparse(uri)
    return Transporter(uri).download(f)


def upload(f, uri):
    return Transporter(uri).upload(f)


def transport(source, destination):
    f = download(source)
    return upload(destination, f)
