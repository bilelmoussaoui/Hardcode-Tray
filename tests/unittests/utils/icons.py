import unittest

from HardcodeTray.utils.icons import replace_to_6hex


class UtilsTests(unittest.TestCase):

    def test_replace_6hex(self):
        self.assertEqual(replace_to_6hex("#000"), "#000000")
        self.assertEqual(replace_to_6hex("#F3A"), "#FF33AA")
        self.assertEqual(replace_to_6hex("#f3a"), "#FF33AA")
        self.assertIsNone(replace_to_6hex("#q11"))
