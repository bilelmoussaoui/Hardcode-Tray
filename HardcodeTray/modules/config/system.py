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
from gettext import gettext as _

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk

from HardcodeTray.const import DESKTOP_ENV
from HardcodeTray.utils import (get_gnome_scaling_factor,
                                get_kde_scaling_factor,
                                get_cinnamon_scaling_factor)
from HardcodeTray.modules.log import Logger
from HardcodeTray.modules.theme import Theme


class SystemConfig:
    """Read your system config."""

    @staticmethod
    def icon_size():
        """Return the icon size."""
        if DESKTOP_ENV in ("pantheon", "xfce"):
            icon_size = 24
        else:
            icon_size = 22
        Logger.debug("System/Icon Size: {}".format(icon_size))
        return icon_size

    @staticmethod
    def scaling_factor():
        """Return the scaling factor."""
        scaling_factor = 1
        # Scaling factor on GNOME desktop
        if DESKTOP_ENV == "gnome":
            scaling_factor = get_gnome_scaling_factor()
        # Cinnamon scaling factor
        elif DESKTOP_ENV == "cinnamon":
            scaling_factor = get_cinnamon_scaling_factor()
        # Scaling factor on KDE Desktop
        elif DESKTOP_ENV == "kde":
            scaling_factor = get_kde_scaling_factor()

        return scaling_factor

    @staticmethod
    def theme():
        """Return a theme object."""
        theme_name = Gtk.Settings.get_default().get_property("gtk-icon-theme-name")
        theme = None
        if theme_name:
            Logger.debug("System/Theme: {}".format(theme_name))
            theme = Theme(theme_name)
        else:
            Logger.error("System/Theme: Not detected.")
        return theme

    @staticmethod
    def action():
        """Return the action to be done."""
        from HardcodeTray.enum import Action
        print(_("1 - Apply"))
        print(_("2 - Revert"))
        print(_("3 - Clear Backup Cache"))
        has_chosen = False
        while not has_chosen:
            try:
                action = int(input(_("Please choose: ")))
                if action not in Action.choices():
                    print(_("Please try again"))
                else:
                    has_chosen = True
                    return action
            except ValueError:
                print(_("Please choose a valid value!"))
            except KeyboardInterrupt:
                exit("")
