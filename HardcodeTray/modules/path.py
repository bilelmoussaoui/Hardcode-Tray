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
from importlib import import_module
from os import path

from HardcodeTray.const import ARCH, USERHOME
from HardcodeTray.utils import get_exact_folder

from HardcodeTray.modules.log import Logger


class Path:
    """
        Path class:
        Check if paths do exists
    """

    DB_VARIABLES = {
        "{userhome}": USERHOME,
        "{size}": 22,
        "{arch}": ARCH,
        "{discord}": "discord_callback",
        "{dropbox}": "dropbox_callback",
        "{hangouts}": "hangouts_callback"
    }

    def __init__(self, absolute_path, parser, path_key):
        self._path = absolute_path
        self._parser = parser
        self.type = path_key
        self._exists = True
        self._validate()

    def __add__(self, filename):
        return self.path + filename

    def __radd__(self, filename):
        return filename + self.path

    def __str__(self):
        return self.path

    @property
    def parser(self):
        """Return Parser instance."""
        return self._parser

    @property
    def path(self):
        """Return the path."""
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def exists(self):
        """Return wether the path exists or not."""
        return self._exists

    def _validate(self):
        """
            Check wether a folder path exists or not.
        """
        from HardcodeTray.app import App

        Path.DB_VARIABLES["{size}"] = str(App.icon_size())

        for key, value in Path.DB_VARIABLES.items():
            if key in self.path:
                if value.endswith("_callback"):  # Check wether it's a function or not
                    self._validate_with_callback(key, value)
                else:
                    self.path = self.path.replace(key, str(value))

        if self.parser.script and self.type == "icons_path":
            binary_file = path.join(self.path, self.parser.binary)
            self._exists = path.exists(self.path) and path.exists(binary_file)
        else:
            self._exists = path.exists(self.path)

    def _validate_with_callback(self, key, callback):
        module = import_module("HardcodeTray.path")
        if hasattr(module, callback):
            method = getattr(module, callback)
            self.path = get_exact_folder(key, self.path, method)
            Logger.debug("Path with condition: "
                         "{} {}".format(callback, self.path))
