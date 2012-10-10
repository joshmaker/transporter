import os
import ftplib
from urlparse import urlparse


class LocalFileAdapter(object):
    """Transporter adapter for working with the local file system
    """

    scheme = "file"
    path = "/"

    def __init__(self, uri=None):
        """Takes a URI in the form of file://initial/file/path/"""
        if uri and isinstance(uri, str):
            uri = urlparse(uri)

        if uri and uri.path:
            self.cd(uri.path)

    def cd(self, path=os.curdir):
        new_path = self.pwd(path)
        if os.path.exists(new_path):
            self.path = new_path
        else:
            raise OSError("Path {0} does not exist".format(new_path))

    def ls(self):
        os.listdir(self.path)

    def mkdir(self, path):
        os.mkdir(self.pwd(path))

    def pwd(self):
        return self.path

    def mv(self, source, destination):
        self.path.rename(self.pwd(source), self.pwd(destination))


class FtpAdapter(object):
    """Transporter adapter for working with FTP servers
    """

    scheme = "ftp"
    connection = ftplib.FTP()

    def __init__(self, uri=None):
        """Takes a URI in the form of ftp://username:password@server.com/"""
        if uri and isinstance(uri, str):
            uri = urlparse(uri)

        if uri:
            self.connect(uri.host)
            self.login(uri.username, uri.password)
            if uri.path:
                self.cd(uri.path)

    def connect(self, host, port=None):
        if self.connection:
            self.disconnect()
        self.connection.connect(host, port)

    def login(self, username, password):
        self.connection.login(user=username, passwd=password)

    def cd(self, path="."):
        self.connection.cwd(path)

    def ls(self):
        return self.connection.nlst()

    def mkdir(self, path):
        self.connection.mkd(path)

    def mv(self, source, destination):
        self.connection.rename(source, destination)

    def rm(self, path):
        return self.connection.delete(path)

    def pwd(self):
        return self.connection.pwd()

    def disconnect(self, host):
        self.connection.quit()
