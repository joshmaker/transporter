import os
import ftplib
from cStringIO import StringIO
from urlparse import urlparse


class AbstractAdapter(object):

    def __init__(self, uri=None):
        """Takes a URI in the form of ftp://username:password@server.com/"""

        if uri and isinstance(uri, str):
            uri = urlparse(uri)

        if uri:
            if uri.hostname:
                self.hostname = uri.hostname
                self.connect(uri.hostname, uri.port)
            else:
                self.hostname = 'localhost'

            if getattr(uri, 'username', False) and getattr(uri, 'password', False):
                self.login(uri.username, uri.password)

            if uri.path:
                self.cd(uri.path)

    def __repr__(self):
        return u'<{0} {1}: {2}>'.format(self.__class__.__name__,
            self.hostname, self.pwd())

    def __del__(self):
        if hasattr(self, 'disconnect'):
            self.disconnect()

    def _open_file_or_string(self, data):
        data_type = type(data)
        if data_type is file:
            return data.read()
        elif data_type is str:
            return data
        else:
            raise NotImplementedError(
                "Unable to extract data from %s, should be str or file" % data_type)


class LocalFileAdapter(AbstractAdapter):
    """Transporter adapter for working with the local file system
    """

    scheme = "file"
    path = "/"

    def cd(self, path="."):
        new_path = os.path.abspath(os.path.join(self.path, path))
        if os.path.exists(new_path):
            self.path = new_path
        else:
            raise OSError("Path {0} does not exist".format(new_path))

    def pwd(self):
        return self.path

    def ls(self):
        os.listdir(self.path)

    def mkdir(self, path):
        os.mkdir(os.path.join(self.pwd(), path))

    def mv(self, source, destination):
        self.path.rename(self.pwd(source), self.pwd(destination))

    def rm(self, path):
        path = os.path.join(self.path, path)
        os.unlink(path)

    def rmdir(self, path):
        path = os.path.join(self.path, path)
        os.rmdir(path)

    def get(self, path):
        path = os.path.join(self.path, path)
        return open(path, 'r+b')

    def put(self, data, path):
        data = self._open_file_or_string(data)
        path = os.path.join(self.path, path)

        new_file = open(path, 'w')
        new_file.write(data)
        new_file.close()
        return new_file


class FtpAdapter(AbstractAdapter):
    """Transporter adapter for working with FTP servers
    """

    scheme = "ftp"
    ftp = None

    def __init__(self, *args, **kwargs):
        super(FtpAdapter, self).__init__(*args, **kwargs)

    def connect(self, host, port=None):
        if self.ftp:
            self.disconnect()

        self.ftp = ftplib.FTP()
        self.ftp.connect(host, port)

    def login(self, username, password):
        self.ftp.login(user=username, passwd=password)

    def cd(self, path="."):
        self.ftp.cwd(path)

    def pwd(self):
        return self.ftp.pwd()

    def ls(self):
        return self.ftp.nlst()

    def mkdir(self, path):
        self.ftp.mkd(os.path.join(self.pwd(), path))

    def mv(self, source, destination):
        self.ftp.rename(source, destination)

    def rm(self, path):
        self.ftp.delete(path)

    def rmdir(self, path):
        self.ftp.rmd(path)

    def get(self, path):
        io = StringIO()
        self.ftp.retrbinary(u'RETR %s' % path, io.write)
        io.seek(0)
        return io

    def put(self, data, path):
        data = StringIO(self._open_file_or_string(data))
        self.ftp.storbinary(u'STOR %s' % os.path.basename(path), data)

    def disconnect(self):
        if self.ftp:
            self.ftp.quit()
            self.ftp = None
