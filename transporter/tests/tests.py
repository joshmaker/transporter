import os
import unittest
import time
import signal
import shutil
# from urlparse import urlparse

from pyftpdlib import ftpserver

from transporter import adapters, Transporter


sample_root = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sandbox')
sample_dir = os.path.join(sample_root, 'dir')


class TestBase(object):

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
        self.adapter.cd(self.root_path)

    def tearDown(self):
        TestBase.tearDownClass()

    def testTesting(self):
        self.assertTrue(True)
        self.assertFalse(False)

    def test_pwd(self):
        self.assertEqual(self.adapter.pwd(), self.root_path)

    def test_cd(self):
        os.mkdir(os.path.join(sample_dir, 'cd_dir'))
        self.adapter.cd('cd_dir')
        self.adapter.cd('..')

        self.assertRaises(Exception, lambda: self.adapter.cd('not_a_dir'))

    def test_mkdir(self):
        self.assertFalse(os.path.exists('new_dir'))
        self.adapter.mkdir('new_dir')

        self.assertTrue(os.path.exists('new_dir'))

    def test_rmdir(self):
        os.mkdir('delete_me')
        self.assertTrue(os.path.exists('delete_me'))
        self.adapter.rmdir('delete_me')

        self.assertFalse(os.path.exists('delete_me'))

    def test_get(self):
        path = os.path.join(sample_dir, 'get_file.txt')
        source_data = self.__create_file(path)
        data = self.adapter.get('get_file.txt')

        self.assertEqual(data.read(), source_data)

    def test_put_str(self):
        data = 'Time: %s' % time.localtime()
        file_name = 'created_from_str.txt'
        self.adapter.put(data, file_name)

        file_path = os.path.join(sample_dir, file_name)
        self.assertTrue(os.path.exists(file_path))
        self.assertEqual(data, open(file_path, 'r').read())

    def test_put_file(self):
        read_path = os.path.join(sample_dir, 'read_from_me.txt')
        write_path = os.path.join(sample_dir, 'write_to_me.txt')
        data = self.__create_file(read_path)
        self.adapter.put(open('read_from_me.txt'), 'write_to_me.txt')

        self.assertTrue(os.path.exists(write_path))
        self.assertEqual(data, open(write_path, 'r').read())

    def __create_file(self, path):
        data = 'Time: %s' % time.time()
        new_file = open(path, 'w')
        new_file.write(data)
        new_file.close()
        return data


class TestLocalFileAdapter(TestBase, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        TestBase.setUpClass()
        cls.root_path = sample_dir
        cls.adapter = adapters.LocalFileAdapter(cls.root_path)


class TestFtpAdapter(TestBase, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root_path = '/dir'

        username = 'user1'
        password = 'passw0rd'
        port = 4452
        host = '127.0.0.1'

        cls.pid = os.fork()
        if cls.pid == 0:
            authorizer = ftpserver.DummyAuthorizer()
            authorizer.add_user(username, password, sample_root, perm="elradfmw")
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
        print cls.pid
        os.kill(cls.pid, signal.SIGTERM)
        os.wait()


if __name__ == '__main__':
    unittest.main()
