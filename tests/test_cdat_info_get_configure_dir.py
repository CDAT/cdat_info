import unittest
import cdat_info
import os
class TestCDATInfo(unittest.TestCase):
    def testGetConfigureDefault(self):
        self.assertEqual(cdat_info.get_configure_directory(),
                         os.path.join(os.path.expanduser("~"), ".cdat"))
    def testGetConfigureEnv(self):
        os.environ["CDAT_CONFIG_DIR"] = "blah"
        self.assertEqual(cdat_info.get_configure_directory(), "blah")
        del(os.environ["CDAT_CONFIG_DIR"])