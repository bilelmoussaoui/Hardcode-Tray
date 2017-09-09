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
from os import path, symlink, remove
from shutil import copyfile

from HardcodeTray.log import Logger


class File:
    """

    """

    def __init__(self, file_path):
        """
        :param file_path: the file absolute path
        """
        self.file_path = file_path

    @property
    def extension(self):
        """
        Get the file extension
        :return: str: file extension (png, svg...)
        """
        return path.splitext(self.file_path)[-1].strip(".").lower()

    @extension.setter
    def extension(self, ext):
        if not self.extension:
            self.file_path = self.file_path + "." + ext

    def create(self):
        """Create the file if not found."""
        if not self.found:
            self.write("")
            return True
        return False

    @property
    def found(self):
        """Return if the file exists or not."""
        return path.isfile(self.file_path)

    @property
    def content(self):
        """Return the  file content."""
        with open(self.file_path, 'r') as file_obj:
            data = file_obj.read()
        return data

    def write(self, content):
        """Write something to the file."""
        with open(self.file_path, 'w') as file_obj:
            file_obj.write(content)

    @property
    def basename(self):
        """Return the file basename."""
        return path.basename(self.file_path)

    def link(self, link_name):
        """Symlink a file, remove the dest file if already exists."""
        try:
            symlink(self.file_path, link_name)
        except FileExistsError:
            remove(link_name)
            self.link(link_name)
        except FileNotFoundError:
            Logger.warning("File not found: {0}".format(self.file_path))

    @property
    def filename(self):
        """Return the filename without the extension."""
        return path.splitext(self.file_path)[0]

    def copy(self, dest, overwrite=False):
        """Copy a file to somewhere else."""
        if overwrite:
            if dest.found:
                dest.remove()
            copyfile(self.file_path, dest)
        elif not overwrite and not path.isfile(dest):
            copyfile(self.file_path, dest)

    def remove(self):
        """Remove the file if found."""
        if self.found:
            return remove(self.file_path)
        return False

    def split(self, key):
        """Split the filename by a string."""
        return self.file_path.split(key)
