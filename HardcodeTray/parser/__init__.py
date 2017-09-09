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
import re
import json

from .database import Database
from .qt import QtDatabase

from HardcodeTray.icon import Icon
from HardcodeTray.fs import Directory, File


class Parser:
    MODULES = {
        "qt": QtDatabase
    }

    def __init__(self):
        self.vars = {}

    def register_callback(self, regex, callback):
        """
        Register a callback to be executed
        Only on paths & if there's a match of the callback
        :param regex: Regex expression
        :param callback: Callable to be executed
        """
        self.vars[regex] = callback

    def parse(self, db_file):
        """
        Parse a database file
        :param db_file: str, the database file path
        :return Database: a database object
        """
        data = {}
        with open(db_file, 'r') as db_obj:
            try:
                data = json.load(db_obj)
            except ValueError:
                print("Corrupted database {}".format(db_file))
            else:
                data['db_file'] = db_file
        if data:
            return self._parse_data(data)
        return None

    def _call_callbacks(self, data_list):
        """
        Call the list of registered callback on paths.
        Allows replacing "{userhome}" like variables into their values
        :param data_list: the data list (app_paths,icons_paths, icons)
        :return: list of valid data.
        """
        data = []
        for item in data_list:
            if isinstance(item, str):
                for pattern, callback in self.vars.items():
                    regex = re.match(pattern, item)
                    if regex and regex.group():
                        item = callback(regex.group(), item)
                if isinstance(item, list):
                    data.extend(item)
                    continue
            data.append(item)
        return data

    def _parse_data(self, data):
        """
        Parse the data and replace it with valid info.
        :param data: dict
        :return: Database of the database file
        """
        for key, value in data.items():
            if isinstance(value, list):
                data[key] = self._call_callbacks(value)
        data["icons"] = Parser.parse_icons(data["icons"])
        data["app_path"] = Parser.parse_app_paths(data["app_path"])
        data["icons_path"] = Parser.parse_icons_paths(data["icons_path"])
        for module_, database in Parser.MODULES.items():
            if data.get("module") and module_ == data["module"]:
                return database(**data)
        return Database(**data)

    @staticmethod
    def parse_icons_paths(icons_paths):
        """
        Parse the icons paths
        :param icons_paths: List of the icons paths
        :return: List of valid icon paths
        """
        icons_paths_ = []
        for icon_path in icons_paths:
            path = Directory(icon_path)
            if path.found:
                icons_paths_.append(path)
        return icons_paths_

    @staticmethod
    def parse_app_paths(app_paths):
        """
        Parse the app paths.
        :param app_paths: list of possible app paths
        :return: list: a list of found paths
        """
        app_paths_ = []
        for app_path in app_paths:
            if app_path[-1] == "/":
                path = Directory(app_path)
            else:
                path = File(app_path)
            if path.found:
                app_paths_.append(path)
        return app_paths_

    @staticmethod
    def parse_icons(icons):
        """
        Parse the icons
        :param icons: List of icons
        :return: list: A list of Icon object
        """
        icons_ = []
        for icon in icons:
            if isinstance(icon, str):
                theme = original = icon
                symlinks = []
            else:
                theme = icon["theme"]
                original = icon["original"]
                symlinks = icon.get("symlinks", [])
            symlinks = [File(symlink) for symlink in symlinks]
            icon = Icon(original, theme, symlinks)
            if icon.found:  # If the icon was found
                icons_.append(icon)
        return icons_
