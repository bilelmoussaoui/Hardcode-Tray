#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.7
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
from src.utils import get_iterated_icons, get_extension

class Icon:
    """
    Icon class, for each icon of each application.

    Args:
        @icon_dic: the icon dictionnary from the json file
        @theme: the current theme
        @default_icon_size: the default icon size
    """

    def __init__(self, icon_dic):
        """Init function."""
        self.icon_data = icon_dic
        self._found = False
        self._read()

    @property
    def found(self):
        return self._found

    @staticmethod
    def get_theme(icon_name):
        """Get the theme to be used dark or light."""
        from src.app import App
        is_dark = "dark" in icon_name.lower()
        if isinstance(App.theme(), dict):
            if is_dark:
                theme = App.theme()["dark"]
            else:
                theme = App.theme()["light"]
        else:
            theme = App.theme()
        return theme

    def _read(self):
        """Get the theme icon,extensions and size. Save all of that to icon."""
        from src.app import App
        if isinstance(self.icon_data, str):
            orig_icon = theme_icon = self.icon_data
        else:
            orig_icon = self.icon_data["original"]
            theme_icon = self.icon_data["theme"]
        ext_orig = get_extension(orig_icon)
        base_name = path.splitext(theme_icon)[0]
        theme = Icon.get_theme(orig_icon)
        theme_icon = theme.lookup_icon(base_name, App.icon_size(), 0)
        if theme_icon:
            self.original = orig_icon
            self.theme = theme_icon.get_filename()
            self.theme_ext = get_extension(self.theme)
            self.orig_ext = ext_orig
            self.icon_size = self.get_icon_size(App.icon_size())
            self._found = True

            if (not isinstance(self.icon_data, str)
                    and self.icon_data.get("symlinks")):
                self.symlinks = get_iterated_icons(self.icon_data["symlinks"])

    def has_symlinks(self):
        """Return if the icon has symlinks or not."""
        return hasattr(self, "symlinks")

    def get_icon_size(self, icon_size):
        """Get the icon size, with hidpi support (depends on the icon name)."""
        icon_name = self.original.split("@")
        if len(icon_name) > 1:
            multiple = int(icon_name[1].split("x")[0])
            if multiple and multiple != 0:
                icon_size *= multiple
        icon_size = path.splitext(self.original)[0].split("-")[-1]
        if icon_size.isdigit():
            icon_size = int(icon_size)
        icon_size = path.splitext(self.original)[0].split("_")[-1]
        if icon_size.isdigit():
            icon_size = int(icon_size)
        return icon_size
