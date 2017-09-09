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
from os import path, makedirs

from HardcodeTray.log import Logger


class Directory:
    """

    """

    def __init__(self, dir_path):
        """
        :param dir_path: the directory absolute path
        """
        self.dir_path = dir_path

    @property
    def found(self):
        return path.isdir(self.dir_path)

    def create(self):
        if not self.found:
            Logger.debug("Creating directory: {}".format(self.dir_path))
            makedirs(self.dir_path, exist_ok=True)
