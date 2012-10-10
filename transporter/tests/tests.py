import os
import unittest
from transporter import adapters
from transporter.transporter import Transporter
from urlparse import urlparse


sample_folder_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample')


class TestLocalFileAdapter(unittest.TestCase):

    def setUp(self):
        self.root_path = sample_folder_path
        os.chdir(self.root_path)

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
        pass


class TestTransporter(unittest.TestCase):
    pass

# dynamically create a test method for each adapter uri
adapter_types = {
    'file://User/': adapters.LocalFileAdapter,
    'ftp://example.com': adapters.FtpAdapter,
}
for uri, cls in adapter_types.items():
    def test_schema(obj):
        trans = Transporter(uri)
        obj.assertIsInstance(trans, cls)
    def_name = 'test_%s_schema' % urlparse(uri).scheme
    setattr(TestTransporter, def_name, test_schema)


if __name__ == '__main__':
    unittest.main()
