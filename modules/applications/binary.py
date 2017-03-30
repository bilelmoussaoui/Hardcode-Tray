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
from modules.applications.application import Application
from modules.utils import backup, revert, create_backup_dir, show_select_backup


class BinaryApplication(Application):
    """Pak Application class, based on data_pak file."""

    def __init__(self, application_data, svgtopng):
        """Init method."""
        Application.__init__(self, application_data, svgtopng)

    def backup_binary(self, icon_path):
        """Backup binary file before modification."""
        backup(self.get_back_dir(), icon_path + self.get_binary())

    def revert_binary(self, icon_path):
        """Restore the backed up binary file."""
        revert(self.get_name(), self.get_selected_back_dir(),
               icon_path + self.get_binary())

    def get_binary(self):
        """Return the binary file if exists."""
        return self.data.data["binary"]

    def reinstall(self):
        """Reinstall the old icons."""
        self.selected_backup = show_select_backup(self.get_name())
        if self.selected_backup:
            self.remove_symlinks()
            for icon_path in self.get_icons_path():
                self.revert_binary(icon_path)
        else:
            self.is_done = False

    def install(self):
        """Install the application icons."""
        self.back_dir = create_backup_dir(self.get_name())
        self.install_symlinks()
        for icon_path in self.get_icons_path():
            self.backup_binary(icon_path)
            for icon in self.get_icons():
                self.install_icon(icon, icon_path)
