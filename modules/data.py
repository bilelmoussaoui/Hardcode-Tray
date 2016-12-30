#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.6.2
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
import json
from modules.utils import create_dir, get_iterated_icons, execute
from modules.const import USERHOME, ARCH
from modules.icon import Icon
absolute_path = path.split(path.abspath(__file__))[0] + "/"


class DataManager:
    """
    DataManager is used to read the json database file.

    It used to create a dictionnary with all the informations about the
    application
    """

    def __init__(self, database_file, theme, default_icon_size,
                 custom_path="", is_only=False):
        """Init function."""
        self.default_icon_size = default_icon_size
        self.json_file = database_file
        self.custom_path = custom_path
        self.is_only = is_only
        self.theme = theme
        self.dont_install = True
        self.supported_icons_cnt = 0
        self.read()

    def get_type(self):
        """Get the type of database(Application) file."""
        if self.data["is_script"]:
            return self.data["script"]
        elif self.data["is_qt"]:
            return "qt"
        else:
            return "normal"

    def get_icons(self):
        """Return the application icons."""
        return self.data["icons"]

    def is_installed(self):
        """Check whether the application is installed or not."""
        return not self.dont_install

    def read(self):
        """Read json file in order to apply the script later."""
        self.data = {}
        if path.isfile(self.json_file):
            with open(self.json_file) as data_file:
                self.data = json.load(data_file)
            if (self.custom_path and self.is_only
                    and path.exists(self.custom_path)):
                self.data["app_path"].append(self.custom_path)
            self.check_paths()
            be_added = (len(self.data["icons_path"]) > 0
                        and len(self.data["app_path"]) > 0)
            if be_added:
                self.dont_install = False
                if isinstance(self.data["icons"], list):
                    self.data["icons"] = get_iterated_icons(self.data["icons"])
                self.get_app_icons()

    def get_app_icons(self):
        """Get a list of icons of each application."""
        if self.is_installed():
            icons = self.get_icons()
            supported_icons = []
            for icon_data in icons:
                if isinstance(icons, list):
                    icon = Icon(icon_data, self.theme, self.default_icon_size)
                else:
                    icon = Icon(icons[icon_data], self.theme,
                                self.default_icon_size)
                if icon.get_is_exists():
                    supported_icons.append(icon.get_data())
                    self.supported_icons_cnt += 1

            self.dont_install = not len(supported_icons) > 0
            self.data["icons"] = supported_icons

    def check_paths(self):
        """
        Check if the app_path exists to detect if the application is installed.

        Also check if the icons path exists, and force creating needed folders.
        See the json key "force_create_folder"
        """
        self.data["app_path"] = list(map(
            self.replace_vars_path, self.data["app_path"]))
        self.data["icons_path"] = list(map(
            self.replace_vars_path, self.data["icons_path"]))
        new_app_path = []
        for app_path in self.data["app_path"]:
            if path.isdir(app_path) or path.isfile(app_path):
                new_app_path.append(app_path)
        self.data["app_path"] = new_app_path
        if not len(self.data["app_path"]) == 0:
            new_icons_path = []
            for icon_path in self.data["icons_path"]:
                if self.data["force_create_folder"]:
                    create_dir(icon_path)
                if path.isdir(icon_path):
                    if ("binary" in self.data.keys()
                            and path.isfile(icon_path + self.data["binary"])):
                        new_icons_path.append(icon_path)
                    else:
                        new_icons_path.append(icon_path)
            self.data["icons_path"] = new_icons_path

    def replace_vars_path(self, _path):
        """Replace common variables informations."""
        if self.data["exec_path_script"]:
            _path = execute([absolute_path + "paths/" +
                             self.data["exec_path_script"], _path],
                            verbose=True).decode("utf-8").strip()
        _path = _path.replace("{userhome}", USERHOME)
        _path = _path.replace("{arch}", ARCH)
        return _path
