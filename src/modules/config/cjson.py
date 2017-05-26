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
from json import load
from os import path

from src.const import CONFIG_FILE, ICONS_SIZE
from src.modules.log import Logger
from src.modules.theme import Theme


class JSONConfig:
    """Read JSON config file and make it usable."""
    _config = None
    _icon_size = None
    _conversion_tool = None
    _blacklist = None
    _nwjs = None
    _theme = None
    _backup_ignore = None

    @staticmethod
    def get_default():
        """Return default instance."""
        if JSONConfig._config is None:
            config = {}
            if path.isfile(CONFIG_FILE):
                Logger.debug("Reading config file: {}".format(CONFIG_FILE))
            with open(CONFIG_FILE, 'r') as data:
                try:
                    config = load(data)
                except ValueError:
                    Logger.warning("The config file is "
                                   "not a valid json file.")
            JSONConfig._config = config
        return JSONConfig._config

    @staticmethod
    def icon_size():
        """Return the icon size in the config file."""
        if JSONConfig._icon_size is None:
            json = JSONConfig.get_default()
            icons = json.get("icons")
            if icons:
                icon_size = icons.get("size")
                Logger.debug("Config/Icon Size: {}".format(icon_size))
                if icon_size not in ICONS_SIZE:
                    Logger.warning("Config/Icon Size: Incorrect.")
                    Logger.debug(
                        "Config/Icon Size: Detected icon size will be used.")
                JSONConfig._icon_size = icon_size
        return JSONConfig._icon_size

    @staticmethod
    def theme():
        """Return theme object set in the config file."""
        if not JSONConfig._theme:
            icons = JSONConfig.get_default().get("icons")
            if icons:
                theme = icons.get("theme", {})
                if isinstance(theme, dict):
                    dark_theme = theme.get("dark")
                    light_theme = theme.get("light")

                if isinstance(theme, str):
                    JSONConfig._theme = Theme(theme)
                    Logger.debug("Config/Theme: {}".format(theme))
                elif dark_theme and light_theme:
                    JSONConfig._theme = {
                        "dark": Theme(dark_theme),
                        "light": Theme(light_theme)
                    }
                    Logger.debug("Config/Dark Theme: {}".format(dark_theme))
                    Logger.debug("Config/Light Theme: {}".format(light_theme))
        return JSONConfig._theme

    @staticmethod
    def conversion_tool():
        """Return conversion tool set in the config file."""
        if not JSONConfig._conversion_tool:
            conversion_tool = JSONConfig.get_default().get("conversion-tool")
            Logger.debug("Config/Conversion Tool: {}".format(conversion_tool))
            JSONConfig._conversion_tool = conversion_tool
        return JSONConfig._conversion_tool

    @staticmethod
    def blacklist():
        """Return a list of blacklist apps."""
        if not JSONConfig._blacklist:
            blacklist = JSONConfig.get_default().get("blacklist", [])
            if blacklist:
                Logger.debug(
                    "Config/Blacklist: {}".format(",".join(blacklist)))
            JSONConfig._blacklist = blacklist
        return JSONConfig._blacklist

    @staticmethod
    def nwjs():
        """Return nwjs sdk path."""
        if not JSONConfig._nwjs:
            nwjs = JSONConfig.get_default().get("nwjs")
            if nwjs and path.exists(nwjs):
                JSONConfig._nwjs = nwjs
                Logger.debug("Config/NWJS SDK: {}".format(nwjs))
        return JSONConfig._nwjs

    @staticmethod
    def backup_ignore():
        """Return a boolean, ignore backup or not."""
        if JSONConfig._backup_ignore is None:
            backup_ignore = JSONConfig.get_default().get("backup-ignore", False)
            Logger.debug("Config/Backup Ignore: {}".format(str(backup_ignore)))
            JSONConfig._backup_ignore = backup_ignore
        return JSONConfig._backup_ignore
