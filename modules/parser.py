#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.6.5
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
from modules.const import ARCH, USERHOME
from modules.icon import Icon
from modules.applications.application import Application
from modules.applications.binary import BinaryApplication
from modules.applications.electron import ElectronApplication
from modules.applications.qt import QtApplication
from modules.applications.pak import PakApplication
from modules.applications.zip import ZipApplication
from modules.applications.nwjs import NWJSApplication
from modules.utils import create_dir, execute, get_iterated_icons, log
from os import path
absolute_path = path.split(path.abspath(__file__))[0] + "/"


class Parser:
    """
    DataManager is used to read the json database file.

    It used to create a dictionnary with all the informations about the
    application
    """
    _APPLICATION_TYPE = {
        "electron" : ElectronApplication,
        "zip" : ZipApplication,
        "pak" : PakApplication,
        "nwjs" : NWJSApplication,
        "qt" : QtApplication,
        "binary" : BinaryApplication,
        "normal" : Application
    }

    def __init__(self, database_file, theme, svgtopng, default_icon_size,
                 custom_path=""):
        """Init function."""
        self.default_icon_size = default_icon_size
        self.json_file = database_file
        self.svgtopng = svgtopng
        self.custom_path = custom_path
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

    def get_application(self):
        """Return the application object."""
        return self._APPLICATION_TYPE[self.get_type()](self, self.svgtopng)

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
            data_file.close()
            if (self.custom_path
                    and path.exists(self.custom_path)):
                self.data["icons_path"].append(self.custom_path)
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
                if (self.data["force_create_folder"] and
                        not path.exists(icon_path)):
                    log("Creating application folder for {0}".format(self.data["name"]))
                    create_dir(icon_path)
                if path.isdir(icon_path):
                    if ("binary" in self.data.keys()
                            and path.isfile(icon_path + self.data["binary"])):
                        new_icons_path.append(icon_path)
                    elif "binary" not in self.data.keys():
                        new_icons_path.append(icon_path)
            self.data["icons_path"] = new_icons_path

    def replace_vars_path(self, _path):
        """Replace common variables informations."""
        old_path = _path
        _path = _path.replace("{userhome}", USERHOME)
        _path = _path.replace("{size}", str(self.default_icon_size))
        _path = _path.replace("{arch}", ARCH)
        if self.data["exec_path_script"]:
            _path = execute([absolute_path + "paths/" +
                             self.data["exec_path_script"], _path],
                            verbose=True).decode("utf-8").strip()
        if _path != old_path:
            log("new application {0} path : {1}".format(self.data["name"], _path))
        return _path
