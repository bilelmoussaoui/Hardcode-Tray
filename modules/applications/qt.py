#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.6.3
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


class QtApplication(Application):
    """Qt application, works only with the patched version of sni-qt."""

    def __init__(self, application_data, svgtopng):
        """Init method."""
        Application.__init__(self, application_data, svgtopng)

    def reinstall(self):
        """Overwrite the reinstall function, and remove the whole dir."""
        for icon_path in self.get_icons_path():
            if path.isdir(icon_path):
                rmtree(icon_path)
