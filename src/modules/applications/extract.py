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
from src.decorators import install_wrapper
from .binary import BinaryApplication


class ExtractApplication(BinaryApplication):

    def __init__(self, parser):
        BinaryApplication.__init__(self, parser)
        self.tmp_data = None

    @install_wrapper
    def install(self):
        """Install the application icons."""
        for icon_path in self.icons_path:
            self.backup_binary(icon_path)
            self.extract(icon_path)
            for icon in self.icons:
                self.install_icon(icon, self.tmp_data)
            self.pack(icon_path)

    def extract(self, icon_path):
        pass

    def pack(self, icon_path):
        pass
