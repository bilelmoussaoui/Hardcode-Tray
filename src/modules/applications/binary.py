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
from .application import Application
from src.utils import backup, revert, create_backup_dir, show_select_backup
from src.decorators import revert_wrapper, install_wrapper

class BinaryApplication(Application):
    """Pak Application class, based on data_pak file."""

    def __init__(self, parser):
        """Init method."""
        Application.__init__(self, parser)

    def backup_binary(self, icon_path):
        """Backup binary file before modification."""
        backup(self.backup_dir, icon_path.append(self.binary))

    def revert_binary(self, icon_path):
        """Restore the backed up binary file."""
        revert(self.name, self.selected_backup,
               icon_path + self.binary)

    @property
    def binary(self):
        """Return the binary file if exists."""
        return self.parser.binary

    @revert_wrapper
    def reinstall(self):
        """Reinstall the old icons."""
        for icon_path in self.icons_path:
            self.revert_binary(icon_path)

    @install_wrapper
    def install(self):
        """Install the application icons."""
        for icon_path in self.icons_path:
            self.backup_binary(icon_path)
            for icon in self.icons:
                self.install_icon(icon, icon_path)
