
import unittest


from HardcodeTray.utils.fs import get_extension


class OSTests(unittest.TestCase):

    def test_get_extension(self):
        """Unittests for get_extension function."""
        self.assertEqual(get_extension("tests.py"), "py")
        self.assertEqual(get_extension("tests.PNG"), "png")
        self.assertEqual(get_extension("tests.hey.svg"), "svg")
        self.assertEqual(get_extension("tests"), "")


if __name__ == "__main__":
    unittest.main()
