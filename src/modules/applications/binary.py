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
from src.modules.applications.application import Application

class BinaryApplication(Application):
    """Pak Application class, based on data_pak file."""

    def __init__(self, parser):
        """Init method."""
        Application.__init__(self, parser)
        self.is_corrupted = False

    @property
    def binary(self):
        """Return the binary file if exists."""
        return self.parser.binary

    def get_backup_file(self, icon_name):
        """Return the binary content of a backup file."""
        backup_file = self.backup.get_backup_file(icon_name)
        if backup_file:
            with open(backup_file, 'rb') as binary_obj:
                pngbytes = binary_obj.read()
            return pngbytes
        return None

    def execute(self, action):
        for icon_path in self.icons_path:
            for icon in self.icons:
                if self.is_corrupted:
                    break
                if action == Action.APPLY:
                    self.install_icon(icon, icon_path)
                elif action == Action.REVERT:
                    self.revert_icon(icon, icon_path)
        self.is_done = not self.is_corrupted
