import os
import unittest
import time
from urlparse import urlparse
import stubserver

from transporter import adapters
from transporter.transporter import Transporter

from StringIO import StringIO
import ftplib


sample_folder_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sandbox')


class TestLocalFileAdapter(unittest.TestCase):

    def setUp(self):
        self.root_path = sample_folder_path
        os.chdir(self.root_path)
        self.adapter = adapters.LocalFileAdapter(self.root_path)
        os.mkdir('%s/directory' % sample_folder_path)

    def tearDown(self):
        os.rmdir('%s/directory' % sample_folder_path)

    def test_pwd(self):
        self.assertEqual(self.adapter.pwd(), self.root_path)

    def test_cd(self):
        fileAdapterA = adapters.LocalFileAdapter(self.root_path)
        fileAdapterB = adapters.LocalFileAdapter(self.root_path)
        self.assertEqual(fileAdapterA.pwd(), fileAdapterB.pwd())

        fileAdapterA.cd('directory')
        os.chdir('directory')

        self.assertNotEqual(fileAdapterA.pwd(), fileAdapterB.pwd())
        self.assertNotEqual(fileAdapterB.pwd(), os.getcwd())
        self.assertEqual(fileAdapterA.pwd(), os.getcwd())

        fileAdapterA.cd('..')
        os.chdir('..')
        self.assertEqual(fileAdapterA.pwd(), os.getcwd())

    def test_mkdir(self):
        new_dir_path = os.path.join(self.root_path, 'new_dir')
        self.assertFalse(os.path.exists(new_dir_path))
        self.adapter.mkdir('new_dir')
        self.assertTrue(os.path.exists(new_dir_path))
        os.rmdir(new_dir_path)

    def test_rmdir(self):
        os.mkdir('delete_me')
        self.assertTrue(os.path.exists('delete_me'))
        self.adapter.rmdir('delete_me')
        self.assertFalse(os.path.exists('delete_me'))

    def test_get(self):
        path = os.path.join(self.root_path, 'created_from_str.txt')
        data = self.__create_file(path)
        self.assertTrue(os.path.exists(path))
        self.assertEqual(self.adapter.get(path).read(), data)
        os.unlink(path)

    def test_put_str(self):
        data = 'Time: %s' % time.localtime()
        file_name = os.path.join(self.root_path, 'created_from_str.txt')
        self.adapter.put(data, file_name)
        self.assertTrue(os.path.exists(file_name))
        self.assertEqual(data, open(file_name, 'r').read())
        os.unlink(file_name)

    def test_put_file(self):
        read_path = os.path.join(self.root_path, 'read_from_me.txt')
        write_path = os.path.join(self.root_path, 'write_to_me.txt')
        data = self.__create_file(read_path)

        self.adapter.put(open(read_path), write_path)
        self.assertTrue(os.path.exists(write_path))
        self.assertEqual(data, open(write_path, 'r').read())
        os.unlink(read_path)
        os.unlink(write_path)

    def __create_file(self, path):
        data = 'Time: %s' % time.localtime()
        new_file = open(path, 'w')
        new_file.write(data)
        new_file.close()
        return data


# TODO update FTPStubServer to allow for more and better tests
class TestTransporter(unittest.TestCase):

    def setUp(self):
        self.server = stubserver.FTPStubServer(6666)
        self.server.run()
        self.adapter = adapters.FtpAdapter('ftp://user1:passwd@localhost:%i' % self.server.port)
        self.assertNotEqual(self.adapter.ftp, None)

    def tearDown(self):
        self.adapter.disconnect()
        self.assertEqual(self.adapter.ftp, None)
        self.server.stop()

# dynamically create a test method for each adapter uri
# to confirm that the correct adapter is used
adapter_types = {
    'file:%s' % sample_folder_path: adapters.LocalFileAdapter,
    'ftp://example.com': adapters.FtpAdapter,
}
for uri, cls in adapter_types.items():
    def test_schema(obj):
        trans = Transporter(uri)
        obj.assertEqual(type(trans.adapter), cls)
    def_name = 'test_%s_schema' % urlparse(uri).scheme
    setattr(TestTransporter, def_name, test_schema)


if __name__ == '__main__':
    unittest.main()
