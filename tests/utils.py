import unittest
from sys import path as sys_path
sys_path.insert(0, '/usr/lib/python3.5/site-packages/')


from HardcodeTray.utils import *


class UtilsTests(unittest.TestCase):

    def test_get_extension(self):
        ext = get_extension("tests.py")
        self.assertEqual(ext, "py")
    
    def test_get_extension_without_one(self):
        ext = get_extension("tests")
        self.assertEqual(ext, "")

    def test_replace_6hex(self):
        color = replace_to_6hex("#000")
        self.assertEqual(color, "#000000")

    def test_invalid_replace_6hex(self):
        color = replace_to_6hex("#q11")
        self.assertIsNone(color)

if __name__ == "__main__":
    unittest.main()