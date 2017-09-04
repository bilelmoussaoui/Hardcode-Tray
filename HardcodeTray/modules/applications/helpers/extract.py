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
from abc import ABCMeta, abstractmethod

from HardcodeTray.enum import Action
from HardcodeTray.modules.applications.helpers.binary import BinaryApplication


class ExtractApplication(BinaryApplication):
    """
        Extractable binary applications.
    """
    __metaclass__ = ABCMeta

    def __init__(self, parser):
        BinaryApplication.__init__(self, parser)


    def execute(self, action):
        """Execute actions: Apply/Revert."""
        for icon_path in self.icons_path:
            if self.is_corrupted:
                break
            self.extract(icon_path) # Extract the file
            for icon in self.icons:
                if action == Action.APPLY:
                    self.install_icon(icon, self.tmp_path)
                elif action == Action.REVERT:
                    self.revert_icon(icon, self.tmp_path)
            self.pack(icon_path) # Pack the file
        self.success = not self.is_corrupted

    @abstractmethod
    def extract(self, icon_path):
        """Extract binary file."""

    @abstractmethod
    def pack(self, icon_path):
        """Pack the binary file."""
