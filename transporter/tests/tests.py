import os
import unittest
import time
import signal
# from urlparse import urlparse

from pyftpdlib import ftpserver

from transporter import adapters


sample_folder_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sandbox')


class TestBase(object):

    def setUp(self):
        print 'setUp'
        os.chdir(sample_folder_path)
        self.adapter.cd(self.root_path)

    def test_pwd(self):
        self.assertEqual(self.adapter.pwd(), sample_folder_path)

    def test_mkdir(self):
        self.assertFalse(os.path.exists('new_dir'))
        self.adapter.mkdir('new_dir')
        self.assertTrue(os.path.exists('new_dir'))
        os.rmdir('new_dir')

    def test_rmdir(self):
        os.mkdir('delete_me')
        self.assertTrue(os.path.exists('delete_me'))
        self.adapter.rmdir('delete_me')
        self.assertFalse(os.path.exists('delete_me'))

    def test_rm(self):
        self.__create_file('rm_test.txt')

    # def test_get(self):
    #     path = os.path.join(sample_folder_path, 'created_from_str.txt')
    #     source_data = self.__create_file(path)
    #     self.assertTrue(os.path.exists(path))
    #     data = self.adapter.get(path)
    #     self.assertEqual(type(data), file)
    #     self.assertEqual(data.read(), source_data)
    #     os.unlink(path)

    # def test_put_str(self):
    #     data = 'Time: %s' % time.localtime()
    #     file_name = os.path.join(sample_folder_path, 'created_from_str.txt')
    #     self.adapter.put(data, file_name)
    #     self.assertTrue(os.path.exists(file_name))
    #     self.assertEqual(data, open(file_name, 'r').read())
    #     os.unlink(file_name)

    # def test_put_file(self):
    #     read_path = os.path.join(sample_folder_path, 'read_from_me.txt')
    #     write_path = os.path.join(sample_folder_path, 'write_to_me.txt')
    #     data = self.__create_file(read_path)

    #     self.adapter.put(open(read_path), write_path)
    #     self.assertTrue(os.path.exists(write_path))
    #     self.assertEqual(data, open(write_path, 'r').read())
    #     os.unlink(read_path)
    #     os.unlink(write_path)

    def __create_file(self, path):
        data = 'Time: %s' % time.time()
        new_file = open(path, 'w')
        new_file.write(data)
        new_file.close()
        return data


class TestLocalFileAdapter(TestBase, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root_path = sample_folder_path
        cls.adapter = adapters.LocalFileAdapter(sample_folder_path)

    def test_cd(self):
        fileAdapterA = adapters.LocalFileAdapter(sample_folder_path)
        fileAdapterB = adapters.LocalFileAdapter(sample_folder_path)
        self.assertEqual(fileAdapterA.pwd(), fileAdapterB.pwd())

        os.mkdir('directory')
        os.mkdir(os.path.join(sample_folder_path, 'directory'))
        fileAdapterA.cd('directory')
        os.chdir('directory')

        self.assertNotEqual(fileAdapterA.pwd(), fileAdapterB.pwd())
        self.assertNotEqual(fileAdapterB.pwd(), os.getcwd())
        self.assertEqual(fileAdapterA.pwd(), os.getcwd())

        fileAdapterA.cd('..')
        os.chdir('..')
        self.assertEqual(fileAdapterA.pwd(), os.getcwd())
        os.rmdir(os.path.join(sample_folder_path, 'directory'))
        os.rmdir('directory')


# TODO update FTPStubServer to allow for more and better tests
class TestFtpAdapter(TestBase, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root_path = '/'

        username = 'user1'
        password = 'passw0rd'
        port = 5021
        host = '127.0.0.1'

        cls.pid = os.fork()
        if cls.pid == 0:
            authorizer = ftpserver.DummyAuthorizer()
            authorizer.add_user(username, password, sample_folder_path, perm="elradfmw")
            handler = ftpserver.FTPHandler
            handler.authorizer = authorizer
            ftpd = ftpserver.FTPServer((host, port), handler)
            ftpd.serve_forever()

        time.sleep(1)

        uri = 'ftp://{user}:{passwd}@{host}:{port}'.format(
                user=username, passwd=password,
                host=host, port=port)
        cls.adapter = adapters.FtpAdapter(uri)

    @classmethod
    def tearDownClass(cls):
        cls.adapter.disconnect()
        cls.assertEqual(cls.adapter.ftp, None)

        os.kill(cls.pid, signal.SIGTERM)
        os.wait()



# class TestTransporter(unittest.TestCase):

#     adapter_map = {
#         'file:%s' % sample_folder_path: adapters.LocalFileAdapter,
#         'ftp://example.com': adapters.FtpAdapter,
#     }

#     def test_schema_selection(self):
#         for uri, cls in self.adapter_map.items():
#             t = Transporter(uri)
#             print 'Testing {0}'.format(uri)
#             self.assertEqual(type(t.adapter), cls)

if __name__ == '__main__':
    unittest.main()
