#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.8
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
from src.decorators import symlinks_installer, revert_wrapper
from src.utils import symlink_file
from .application import Application

class QtApplication(Application):
    """Qt application, works only with the patched version of sni-qt."""
    BACKUP_IGNORE = True

    def __init__(self, parser):
        """Init method."""
        Application.__init__(self, parser)

    @symlinks_installer
    def install_icon(self, icon, icon_path):
        """Install icon to the current directory."""
        base_icon = icon.original
        theme_icon = icon.theme
        ext_theme = icon.theme_ext
        output_icon = '{0}.{1}'.format(icon_path.append(base_icon), ext_theme)
        symlink_file(theme_icon, output_icon)

    @revert_wrapper
    def reinstall(self):
        """Overwrite the reinstall function, and remove the whole dir."""
        for icon_path in self.icons_path:
            if path.isdir(icon_path):
                rmtree(icon_path)
