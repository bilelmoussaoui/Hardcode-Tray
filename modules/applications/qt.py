#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.6.4
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
from shutil import rmtree
from modules.applications.application import Application
from modules.utils import symlink_file


class QtApplication(Application):
    """Qt application, works only with the patched version of sni-qt."""

    def __init__(self, application_data, svgtopng):
        """Init method."""
        super(QtApplication, self).__init__(application_data, svgtopng)

    @staticmethod
    def install_icon(icon, icon_path):
        """Install icon to the current directory."""
        base_icon = icon["original"]
        theme_icon = icon["theme"]
        ext_theme = icon["theme_ext"]
        output_icon = '%s.%s' % (icon_path + base_icon, ext_theme)
        symlink_file(theme_icon, output_icon)
        if "symlinks" in icon.keys():
            for symlink_icon in icon["symlinks"]:
                symlink_file(output_icon, '%s.%s' %
                             (icon_path + symlink_icon, ext_theme))

    def reinstall(self):
        """Overwrite the reinstall function, and remove the whole dir."""
        for icon_path in self.get_icons_path():
            if path.isdir(icon_path):
                rmtree(icon_path)
