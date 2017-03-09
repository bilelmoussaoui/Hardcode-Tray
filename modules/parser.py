#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.6.6
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
import logging
from os import path

from modules.const import ARCH, USERHOME, DESKTOP_ENV
from modules.icon import Icon
from modules.theme import Theme
from modules.applications.application import Application
from modules.applications.binary import BinaryApplication
from modules.applications.electron import ElectronApplication
from modules.applications.qt import QtApplication
from modules.applications.pak import PakApplication
from modules.applications.zip import ZipApplication
from modules.applications.nwjs import NWJSApplication
from modules.svg.inkscape import Inkscape
from modules.svg.svgcairo import CairoSVG
from modules.svg.rsvgconvert import RSVGConvert
from modules.svg.imagemagick import ImageMagick
from modules.svg.svgexport import SVGExport
from modules.svg.svg import SVGNotInstalled
from modules.utils import (
    create_dir, execute, get_scaling_factor, get_iterated_icons, replace_to_6hex)
from gi.repository import Gio


logging = logging.getLogger('hardcode-tray')
absolute_path = path.split(path.abspath(__file__))[0] + "/"
CONVERSION_TOOLS = {"Inkscape": Inkscape,
                    "CairoSVG": CairoSVG,
                    "RSVGConvert": RSVGConvert,
                    "ImageMagick": ImageMagick,
                    "SVGExport": SVGExport
                   }


class Parser:
    """
    DataManager is used to read the json database file.

    It used to create a dictionnary with all the informations about the
    application
    """
    _APPLICATION_TYPE = {
        "electron": ElectronApplication,
        "zip": ZipApplication,
        "pak": PakApplication,
        "nwjs": NWJSApplication,
        "qt": QtApplication,
        "binary": BinaryApplication,
        "normal": Application
    }

    def __init__(self, database_file, args):
        """Init function."""
        self.default_icon_size = args.icon_size
        self.json_file = database_file
        self.svgtopng = args.svgtopng
        self.custom_path = args.path
        self.theme = args.theme
        self.dont_install = True
        self.supported_icons_cnt = 0
        self.read()

    def get_type(self):
        """Get the type of database(Application) file."""
        if self.data["is_script"]:
            return self.data["script"]
        elif self.data["is_qt"]:
            return "qt"
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
                    logging.debug(
                        "Creating application folder for %s", self.data["name"])
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
            script_path = path.join(
                absolute_path, "paths", self.data["exec_path_script"])
            if path.exists(script_path):
                _path = execute([script_path, _path],
                                verbose=True).decode("utf-8").strip()
            else:
                logging.error("Script file `%s` not found", script_path)
        if _path != old_path:
            logging.debug("new application %s path : %s", self.data["name"], _path)
        return _path


class ArgsParser:
    """CLI arguments parser."""

    def __init__(self, args):
        self._args = args
        self._parse()

    def _parse(self):
        """Parse arguments in seperate functions."""
        self._parse_theme()
        self._parse_colors()
        self._parse_conversion_tool()
        self._parse_icon_size()
        self._parse_scaling_factor()
        self._parse_fix_only()
        self._parse_path()
        self._parse_choice()

    @property
    def args(self):
        """Property : args."""
        return self._args

    def _parse_theme(self):
        if self.args.theme:
            self.theme = Theme(self.args.theme)
        elif self.args.light_theme and self.args.dark_theme:
            self.theme = {
                "dark": Theme(self.args.dark_theme),
                "light": Theme(self.args.light_theme)
            }
        else:
            source = Gio.SettingsSchemaSource.get_default()
            if source.lookup("org.gnome.desktop.interface", True):
                gsettings = Gio.Settings.new("org.gnome.desktop.interface")
                theme_name = gsettings.get_string("icon-theme")
                self.theme = Theme(theme_name)

    def _parse_colors(self):
        self.colours = []
        if self.args.change_color:
            list_colours = self.args.change_color
            colours = []
            for color in list_colours:
                color = color.strip().split(" ")
                to_replace = replace_to_6hex(color[0])
                for_replace = replace_to_6hex(color[1])
                colours.append([to_replace, for_replace])
            self.colours = colours

    def _parse_conversion_tool(self):
        if self.args.conversion_tool:
            try:
                self.svgtopng = CONVERSION_TOOLS[
                    self.args.conversion_tool](self.colours)
            except SVGNotInstalled:
                exit("The selected conversion tool is not installed.")
        else:
            svgtool_found = False
            for conversion_tool in CONVERSION_TOOLS:
                try:
                    self.svgtopng = CONVERSION_TOOLS[
                        conversion_tool](self.colours)
                    svgtool_found = True
                    break
                except SVGNotInstalled:
                    svgtool_found = False

            if not svgtool_found:
                raise SVGNotInstalled

    def _parse_icon_size(self):
        if self.args.size:
            self.icon_size = self.args.size
        else:
            if DESKTOP_ENV in ("pantheon", "xfce"):
                self.icon_size = 24
            else:
                self.icon_size = 22

    def _parse_scaling_factor(self):
        self.scaling_factor = get_scaling_factor(DESKTOP_ENV)
        if self.scaling_factor > 1:
            self.icon_size = round(self.icon_size * self.scaling_factor, 0)
            logging.debug("Icon size was changed to : %s", self.icon_size)

    def _parse_fix_only(self):
        self.only = []
        if self.args.only:
            self.only = self.args.only.lower().strip().split(",")

    def _parse_path(self):
        self.path = None
        if self.args.path and len(self.only) != 0:
            proposed_path = self.args.path
            if path.exists(proposed_path) and path.isdir(proposed_path):
                self.path = self.args.path
            else:
                raise FileNotFoundError("Please select a valid --path")

    def _parse_choice(self):
        self.choice = None
        if self.args.apply and self.args.revert:
            raise ValueError
        if self.args.apply:
            self.choice = 1
        elif self.args.revert:
            self.choice = 2
