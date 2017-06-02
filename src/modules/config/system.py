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
from gi.repository import Gio

from src.const import DESKTOP_ENV, THEME_CONFIG
from src.utils import get_scaling_factor
from src.modules.log import Logger
from src.modules.theme import Theme


class SystemConfig:
    """Read your system config."""
    _icon_size = None
    _theme = None
    _action = None
    _scaling_factor = None

    @staticmethod
    def icon_size():
        """Return the icon size."""
        if SystemConfig._icon_size is None:
            if DESKTOP_ENV in ("pantheon", "xfce"):
                icon_size = 24
            else:
                icon_size = 22
            Logger.debug("System/Icon Size: {}".format(icon_size))
            SystemConfig._icon_size = icon_size
        return SystemConfig._icon_size

    @staticmethod
    def scaling_factor():
        """Return the scaling factor."""
        if SystemConfig._scaling_factor is None:
            scaling_factor = get_scaling_factor(DESKTOP_ENV)
            SystemConfig._scaling_factor = scaling_factor
        return SystemConfig._scaling_factor

    @staticmethod
    def theme():
        """Return a theme object."""
        if SystemConfig._theme is None:
            try:
                theme = THEME_CONFIG[DESKTOP_ENV]
            except KeyError:
                theme = THEME_CONFIG["gnome"]
            key, path = theme["key"], theme["path"]
            source = Gio.SettingsSchemaSource.get_default()
            if source.lookup(path, True):
                gsettings = Gio.Settings.new(path)
                theme_name = gsettings.get_string(key)
                SystemConfig._theme = Theme(theme_name)
                Logger.debug("System/Theme: {}".format(theme_name))
            else:
                Logger.error("System/Theme: Not detected.")
        return SystemConfig._theme

    @staticmethod
    def action():
        """Return the action to be done."""
        if SystemConfig._action is None:
            from src.enum import Action
            print("1 - Apply")
            print("2 - Revert")
            print("3 - Clear Backup Cache")
            has_chosen = False
            while not has_chosen:
                try:
                    action = int(input("Please choose: "))
                    if action not in Action.choices():
                        print("Please try again")
                    else:
                        has_chosen = True
                        SystemConfig._action = action
                except ValueError:
                    print("Please choose a valid value!")
                except KeyboardInterrupt:
                    exit("")
        return SystemConfig._action
