"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Website : https://github.com/bil-elmoussaoui/Hardcode-Tray
Licence : The script is released under GPL, uses a modified script
     form Chromium project released under BSD license
This file is part of Hardcode-Tray.
Hardcode-Tray is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Hardcode-Tray is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Hardcode-Tray. If not, see <http://www.gnu.org/licenses/>.
"""
from os import path
import tempfile
import unittest

from HardcodeTray.fs.file import File


class FileTests(unittest.TestCase):
    """ File Class tests."""

    def test_extension(self):
        """Test if File returns the correct extension."""
        self.assertEqual(File("test.png").extension, "png")
        self.assertEqual(File("test.PNG").extension, "png")
        self.assertEqual(File("test").extension, "")
        self.assertEqual(File("Hello.test.png").extension, "png")

    def test_found(self):
        """Test if the found property returns the correct value."""
        self.assertEqual(File("./file_tests.py").found, True)
        self.assertEqual(File("../").found, False)
        self.assertEqual(File("./test.png").found, False)

    def test_remove(self):
        """Test if file creation/remove works correctly."""
        tmp_file = File(path.join(tempfile.gettempdir(), "test_remove"))
        tmp_file.create()
        self.assertEqual(tmp_file.found, True)
        tmp_file.remove()
        self.assertEqual(tmp_file.found, False)


unittest.main()
