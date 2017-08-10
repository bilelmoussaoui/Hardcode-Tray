import unittest

from HardcodeTray.utils.dict import *


class DictTests(unittest.TestCase):


    def test_get_from_dict(self):
        data = {"files": {
            "tests": {
                "first": "utils"
            }
        }}
        self.assertEqual(get_from_dict(data, ["files", "tests", "first"]),
                         "utils")
        self.assertIsNone(get_from_dict(data, ["files", "tests", "utils"]))

    def test_set_in_dict(self):
        data = {"files": {
            "tests": {
                "first": "utils"
            }
        }}
        set_in_dict(data, ["files", "tests"], "hey")
        self.assertEqual(data, {"files": {"tests": "hey"}})

        set_in_dict(data, ["files", "hey"], "empty")
        self.assertEqual(data, {'files': {'hey': 'empty', 'tests': 'hey'}})


if __name__ == "__main__":
    unittest.main()
