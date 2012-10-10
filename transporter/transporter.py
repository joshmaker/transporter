from urlparse import urlparse
import os
import adapters


try:
    import paramiko
except ImportError:
    pass

__all__ = ["download", "upload", "transport", "Transporter"]

"""The following protocals are supported ftp, ftps, http and https.
sftp and ssh require paramiko to be installed
"""


class Transporter(object):

    availible_adapters = {
        "ftp": adapters.FtpAdapter,
        "ftps": adapters.FtpAdapter,
        "file": adapters.LocalFileAdapter
    }
    adaptor = None

    def __init__(self, uri):
        uri = urlparse(uri)
        if uri.scheme not in self.availible_adaptors:
            msg = "{0} is not a support scheme. Availible schemes: {1}".format(
                    uri.scheme, [s for s in self.availible_adaptors])
            raise NotImplemented(msg)

        self.adaptor = self.availible_adaptors[uri.scheme](uri)

    def __getattr__(self, attr):
        return getattr(self.adaptor, attr)


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
