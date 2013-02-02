import os
import unittest
import time
import signal
import shutil
from urlparse import urlparse

from pyftpdlib import ftpserver

import transporter


sample_root = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'sandbox')
sample_dir = os.path.join(sample_root, 'dir')


class TestBase(object):

    transporter = None

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(sample_dir):
            os.mkdir(sample_dir)
        os.chdir(sample_dir)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(sample_dir):
            shutil.rmtree(sample_dir)

    def setUp(self):
        TestBase.setUpClass()
        self.transporter.cd(self.root_path)

    def tearDown(self):
        TestBase.tearDownClass()

    def testTesting(self):
        self.assertTrue(True)
        self.assertFalse(False)

    def test_pwd(self):
        self.assertEqual(self.transporter.pwd(), self.root_path)
        os.mkdir('test_folder')
        self.transporter.cd('test_folder')
        self.assertNotEqual(self.transporter.pwd(), self.root_path)
        self.assertEqual(self.transporter.pwd(),
            os.path.join(self.root_path, 'test_folder'))

    def test_cd(self):
        os.mkdir(os.path.join(sample_dir, 'cd_dir'))
        self.transporter.cd('cd_dir')
        self.transporter.cd('..')

        self.assertRaises(Exception,
                lambda: self.transporter.cd('not_a_dir'))

    def test_ls(self):
        self.assertEqual(self.transporter.ls(), [])
        os.mkdir('ls_dir')
        self.__create_file('ls_file')
        self.assertEqual(self.transporter.ls(), ['ls_dir', 'ls_file'])

    def test_mkdir(self):
        self.assertFalse(os.path.exists('new_dir'))
        self.transporter.mkdir('new_dir')

        self.assertTrue(os.path.exists('new_dir'))

    def test_rmdir(self):
        os.mkdir('delete_me')
        self.assertTrue(os.path.exists('delete_me'))
        self.transporter.rmdir('delete_me')

        self.assertFalse(os.path.exists('delete_me'))

    def test_mv(self):
        os.mkdir('lock')
        self.__create_file('key.txt')
        final_path = os.path.join(sample_dir, 'lock', 'key.txt')

        self.assertFalse(os.path.exists(final_path))
        self.transporter.mv('key.txt', os.path.join('lock', 'key.txt'))
        self.assertTrue(os.path.exists(final_path))

    def test_get(self):
        path = os.path.join(sample_dir, 'get_file.txt')
        source_data = self.__create_file(path)
        data = self.transporter.get('get_file.txt')

        self.assertEqual(data.read(), source_data)

    def test_put_str(self):
        data = 'Time: %s' % time.localtime()
        file_name = 'created_from_str.txt'
        self.transporter.put(data, file_name)

        file_path = os.path.join(sample_dir, file_name)
        self.assertTrue(os.path.exists(file_path))
        self.assertEqual(data, open(file_path, 'r').read())

    def test_put_file(self):
        read_path = os.path.join(sample_dir, 'read_from_me.txt')
        write_path = os.path.join(sample_dir, 'write_to_me.txt')
        data = self.__create_file(read_path)
        self.transporter.put(open('read_from_me.txt'), 'write_to_me.txt')

        self.assertTrue(os.path.exists(write_path))
        self.assertEqual(data, open(write_path, 'r').read())

    def __create_file(self, path):
        data = 'Time: %s' % time.time()
        new_file = open(path, 'w')
        new_file.write(data)
        new_file.close()
        return data


class TestLocalFileAdapter(TestBase, unittest.TestCase):

    uri = sample_dir
    root_path = sample_dir

    @classmethod
    def setUpClass(cls):
        TestBase.setUpClass()
        cls.transporter = transporter.Transporter(cls.uri)

    def test_adapter_type(self):
        self.assertEqual(type(self.transporter.adapter), 
            transporter.adapters.LocalFileAdapter)


class TestFtptransporter(TestBase, unittest.TestCase):

    uri = 'ftp://user1:pA$$w0rd@127.0.0.1:8021'
    root_path = '/dir'

    @classmethod
    def setUpClass(cls):
        cls.pid = os.fork()
        if cls.pid == 0:
            uri = urlparse(cls.uri)
            authorizer = ftpserver.DummyAuthorizer()
            authorizer.add_user(uri.username, uri.password,
                    sample_root, perm="elradfmw")
            handler = ftpserver.FTPHandler
            handler.authorizer = authorizer
            ftpd = ftpserver.FTPServer((uri.hostname, uri.port), handler)
            ftpd.serve_forever()
        time.sleep(0.5)
        cls.transporter = transporter.Transporter(cls.uri)

    @classmethod
    def tearDownClass(cls):
        cls.transporter.disconnect()
        os.kill(cls.pid, signal.SIGTERM)
        os.wait()

    def test_adapter_type(self):
        self.assertEqual(type(self.transporter.adapter), 
            transporter.adapters.FtpAdapter)

if __name__ == '__main__':
    unittest.main()
