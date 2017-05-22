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
import json
from src.utils import get_iterated_icons
from src.enum import ApplicationType
from .icon import Icon
from .path import Path
from .applications import *


class Parser:
    """
        Parse Json database file
    """

    def __init__(self, db_file):
        self._db_file = db_file
        self.app_path = []
        self.icons_path = []
        self.is_script = False
        self.is_qt = False
        self.script = None
        self.exec_path_script = None
        self.icons = []  # List of icons per app
        self.total_icons = 0
        # By default the app is not installed on the user's system
        self.dont_install = True
        self._read()

    def get_type(self):
        """Get the type of database(Application) file."""
        if hasattr(self, "is_script") and self.is_script:
            return self.script
        elif hasattr(self, "is_qt") and self.is_qt:
            return "qt"
        return "normal"

    def is_installed(self):
        return not self.dont_install

    def get_application(self):
        application = ApplicationType.choices()[self.get_type()]
        return globals()[application](self)

    def _read(self):
        """
            Read the json file and parse it.
        """
        with open(self._db_file, 'r') as f:
            data = json.load(f)
            do_later = ["app_path", "icons_path", "icons"]
            for key, value in data.items():
                if key not in do_later:
                    setattr(self, key, value)
        f.close()
        self._parse_paths(data["app_path"], "app_path")
        self._parse_paths(data["icons_path"], "icons_path")
        self._parse_icons(data["icons"])

        self.dont_install = not (len(self.icons) > 0
                                 and len(self.app_path) > 0
                                 and len(self.icons_path) > 0
                                 )

    def _parse_paths(self, paths, key="app_path"):
        for path in paths:
            path = Path(path, self.exec_path_script)
            if path.found:  # If path exists
                getattr(self, key).append(path)

    def _parse_icons(self, icons):
        if isinstance(icons, list):
            icons = get_iterated_icons(icons)
        for icon in icons:
            if isinstance(icons, list):
                icon = Icon(icon)
            else:
                icon = Icon(icons[icon])
            if icon.found:  # If icon found on current Gtk Icon theme
                self.icons.append(icon)
                self.total_icons += 1
