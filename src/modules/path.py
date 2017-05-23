#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.8
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
from src.const import ARCH, PATH_SCRIPTS_FOLDER, USERHOME
from src.utils import create_dir, execute
from src.modules.log import Logger


class Path:
    """
        Path class:
        Check if paths do exists
    """

    DB_VARIABLES = {
        "{userhome}": USERHOME,
        "{size}": 22,
        "{arch}": ARCH
    }

    def __init__(self, absolute_path, parser, path_key):
        self._path = absolute_path
        self._parser = parser
        self.type = path_key
        self._exists = True
        self._validate()

    def append(self, filename):
        """Append a file name to the path."""
        return path.join(self.path, filename)

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
        from src.app import App
        Path.DB_VARIABLES["{size}"] = App.icon_size()
        for key, value in Path.DB_VARIABLES.items():
            self.path = self.path.replace(key, str(value))
        if self.parser.exec_path_script:
            # If application does need a specific script to get the right path
            script_path = path.join(PATH_SCRIPTS_FOLDER, self.parser.exec_path_script)
            if path.exists(script_path):
                self.path = execute([script_path, self.path],
                                    verbose=True).decode("utf-8").strip()
            else:
                Logger.error("Script file `{0}` not found".format(script_path))
        if self.parser.force_create_folder and self.type == "icons_path":
            create_dir(self.path)

        if self.parser.is_script and self.type == "app_path":
            binary_file = path.join(self.path, self.parser.binary)
            if not path.exists(self.path) or not path.exists(binary_file):
                self._exists = False
        else:
            if not path.exists(self.path):
                self._exists = False
