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
from src.enum import Action
from src.modules.applications.binary import BinaryApplication


class ExtractApplication(BinaryApplication):
    """
        Extractable binary applications.
    """

    def __init__(self, parser):
        BinaryApplication.__init__(self, parser)
        self.tmp_data = None

    def execute(self, action):
        """Execute actions: Apply/Revert."""
        for icon_path in self.icons_path:
            if self.is_corrupted:
                break
            self.extract(icon_path)
            for icon in self.icons:
                if action == Action.APPLY:
                    self.install_icon(icon, self.tmp_data)
                elif action == Action.REVERT:
                    self.revert_icon(icon, self.tmp_data)
            self.pack(icon_path)
        self.is_done = not self.is_corrupted

    def extract(self, icon_path):
        """Extract binary file."""
        pass

    def pack(self, icon_path):
        """Pack the binary file."""
        pass
