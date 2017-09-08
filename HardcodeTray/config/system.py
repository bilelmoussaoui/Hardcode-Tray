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
from HardcodeTray.utils.scaling_factor import *
from HardcodeTray.log import Logger
from HardcodeTray.theme import Theme


class SystemConfig:
    """Read your system config."""

    def __init__(self):
        self.data = {}
        self.parse_data()

    def parse_data(self):
        """Parse the System config data and store it."""
        self.data["icon_size"] = self.icon_size
        self.data["scaling_factor"] = self.scaling_factor
        self.data["theme"] = self.theme

    @property
    def icon_size(self):
        """Return the icon size."""
        if DESKTOP_ENV in ("pantheon", "xfce"):
            icon_size = 24
        else:
            icon_size = 22
        Logger.debug("System/Icon Size: {}".format(icon_size))
        return icon_size

    @property
    def scaling_factor(self):
        """Return the scaling factor."""
        scaling_factor = 1
        # Scaling factor on GNOME desktop
        if DESKTOP_ENV == "gnome":
            scaling_factor = gnome_scaling_factor()
        # Cinnamon scaling factor
        elif DESKTOP_ENV == "cinnamon":
            scaling_factor = cinnamon_scaling_factor()
        # Scaling factor on KDE Desktop
        elif DESKTOP_ENV == "kde":
            scaling_factor = kde_scaling_factor()

        return scaling_factor

    @property
    def theme(self):
        """Return a theme object."""
        theme_name = Gtk.Settings.get_default().get_property("gtk-icon-theme-name")
        theme = None
        if theme_name:
            Logger.debug("System/Theme: {}".format(theme_name))
            theme = Theme(theme_name)
        else:
            Logger.error("System/Theme: Not detected.")
        return theme
