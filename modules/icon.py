#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.6
Website : https://github.com/bil-elmoussaoui/Hardcode-Tray
Licence : The script is released under GPL, uses a modified script
     form Chromium project released under BSD license
This file is part of Hardcode-Tray.
Hardcode-Tray is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
TwoFactorAuth is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Hardcode-Tray. If not, see <http://www.gnu.org/licenses/>.
"""
from os import path
from modules.utils import get_iterated_icons, get_extension


class Icon:

    def __init__(self, icon_dic, theme, default_icon_size):
        self.default_icon_size = default_icon_size
        self.icon_data = icon_dic
        self.theme = theme
        self.icon = {}
        self.is_exists = False
        self.read()

    def read(self):
        if isinstance(self.icon_data, str):
            orig_icon = theme_icon = self.icon_data
        else:
            orig_icon = self.icon_data["original"]
            theme_icon = self.icon_data["theme"]
        ext_orig = get_extension(orig_icon)
        base_name = path.splitext(theme_icon)[0]
        # TODO: Fix get_theme function
        theme_icon = self.theme.lookup_icon(base_name,
                                            self.default_icon_size, 0)
        if theme_icon:
            self.icon["original"] = orig_icon
            self.icon["theme"] = theme_icon.get_filename()
            self.icon["theme_ext"] = get_extension(self.icon["theme"])
            self.icon["orig_ext"] = ext_orig
            self.icon["icon_size"] = self.get_icon_size()
            self.is_exists = True

            if not isinstance(self.icon_data, str):
                if "symlinks" in self.icon_data.keys():
                    self.icon["symlinks"] = get_iterated_icons(
                        self.icon_data["symlinks"])

    def get_is_exists(self):
        return self.is_exists

    def get_data(self):
        return self.icon

    def get_icon_size(self):
        """Get the icon size, with hidpi support (depends on the icon name)."""
        icon_size = self.default_icon_size
        icon_name = self.icon["original"].split("@")
        if len(icon_name) > 1:
            multiple = int(icon_name[1].split("x")[0])
            if multiple and multiple != 0:
                icon_size *= multiple
        icon_size = path.splitext(self.icon["original"])[0].split("-")[-1]
        if icon_size.isdigit():
            icon_size = int(icon_size)

        return icon_size
