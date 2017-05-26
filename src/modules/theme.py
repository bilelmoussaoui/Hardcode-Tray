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
from gi import require_version

from src.const import THEMES_LIST

require_version("Gtk", "3.0")
from gi.repository import Gtk


class Theme(Gtk.IconTheme):
    """Easy way to create new themes based on the theme name."""

    def __init__(self, theme_name):
        if theme_name not in THEMES_LIST:
            exit("Theme {} does not exists.".format(theme_name))

        self._name = theme_name
        Gtk.IconTheme.__init__(self)
        self.set_custom_theme(self.name)

    @property
    def name(self):
        """Property: name."""
        return self._name

    def __getattr__(self, item):
        if isinstance(self.name, dict):
            return self.name[item]

    def __repr__(self, *args):
        return self.name
