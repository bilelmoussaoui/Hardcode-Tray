#!/usr/bin/python3
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
from __future__ import absolute_import

from json import load
from os import path

from src.const import CONFIG_FILE, ICONS_SIZE
from src.modules.log import Logger
from src.modules.theme import Theme


class JSONConfig:
    """Read JSON config file and make it usable."""

    def __init__(self):
        self.icons = {}
        self._backup_ignore = False
        self._blacklist = []
        self._conversion_tool = None
        self._nwjs = None
        self._scaling_factor = 1
        self._read()

    def _read(self):
        """Read the config file."""
        if path.isfile(CONFIG_FILE):
            Logger.debug("Reading config file: {}".format(CONFIG_FILE))
            with open(CONFIG_FILE, 'r') as data:
                try:
                    config = load(data)
                    for key, value in config.items():
                        setattr(self, "_" + key, value)
                except ValueError:
                    Logger.warning("The config file is "
                                   "not a valid json file.")
        else:
            Logger.debug("Config file: Not found.")


    def icon_size(self):
        """Return the icon size in the config file."""
        icon_size = None
        if self.icons:
            icon_size = self.icons.get("size")
            Logger.debug("Config/Icon Size: {}".format(icon_size))
            if icon_size not in ICONS_SIZE:
                Logger.warning("Config/Icon Size: Incorrect.")
                Logger.debug("Config/Icon Size: Detected icon "
                             "size will be used.")
        return icon_size

    def theme(self):
        """Return theme object set in the config file."""
        theme_obj = None
        if self.icons:
            theme = self.icons.get("theme", {})
            if isinstance(theme, dict):
                dark_theme = theme.get("dark")
                light_theme = theme.get("light")

            if isinstance(theme, str):
                theme_obj = Theme(theme)
                Logger.debug("Config/Theme: {}".format(theme))
            elif dark_theme and light_theme:
                theme_obj = Theme.new_with_dark_light(dark_theme, light_theme)

                Logger.debug("Config/Dark Theme: {}".format(dark_theme))
                Logger.debug("Config/Light Theme: {}".format(light_theme))
        return theme_obj

    def conversion_tool(self):
        """Return conversion tool set in the config file."""
        conversion_tool = self._conversion_tool
        Logger.debug("Config/Conversion Tool: {}".format(conversion_tool))
        return conversion_tool

    def blacklist(self):
        """Return a list of blacklist apps."""
        blacklist = self._blacklist
        if blacklist:
            Logger.debug("Config/Blacklist: "
                         "{}".format(",".join(blacklist)))
        return blacklist

    def nwjs(self):
        """Return nwjs sdk path."""
        nwjs = self._nwjs
        if nwjs and path.exists(nwjs):
            Logger.debug("Config/NWJS SDK: {}".format(nwjs))
            return nwjs
        return None

    def scaling_factor(self):
        """Return widget scaling factor."""
        if self._scaling_factor and self._scaling_factor > 1:
            return self._scaling_factor
        return 1

    def backup_ignore(self):
        """Return a boolean, ignore backup or not."""
        backup_ignore = self._backup_ignore
        Logger.debug("Config/Backup Ignore: {}".format(str(backup_ignore)))
        return backup_ignore
