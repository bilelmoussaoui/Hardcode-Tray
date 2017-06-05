#!/usr/bin/python3
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
from os import path

from src.modules.applications.helpers.binary import BinaryApplication
from src.modules.applications.helpers.asar import AsarFile
from src.modules.log import Logger
from src.utils import get_pngbytes


class ElectronApplication(BinaryApplication):
    """Electron applicaton object."""

    def __init__(self, parser):
        """Use the parent class, Application, modify only the (re)install."""
        BinaryApplication.__init__(self, parser)

    def install_icon(self, icon, icon_path):
        """Install the icon."""
        pngbytes = get_pngbytes(icon)
        if pngbytes:
            icon_path = ElectronApplication.get_real_path(icon.original)
            self.set_icon(icon_path, icon_path, pngbytes, True)
        else:
            Logger.error("PNG file was not found.")

    @staticmethod
    def get_real_path(icon_name):
        """Get real path of an icon name inside the asar file."""
        return "files/{0}".format("/files/".join(icon_name.split("/")))

    def revert_icon(self, icon, icon_path):
        """Revert to the original icon."""
        asar_icon_path = ElectronApplication.get_real_path(icon.original)
        backup_file = "|".join(asar_icon_path.split("/"))

        pngbytes = self.get_backup_file(backup_file)
        if pngbytes:
            self.set_icon(icon.original, icon_path, pngbytes)
        else:
            Logger.error("Backup file of {0} was not found".format(self.name))

    def set_icon(self, icon_to_repl, binary_path, pngbytes, backup=False):
        """Set the icon into the electron binary file."""
        binary_file = path.join(str(binary_path), self.binary)

        asar = AsarFile(binary_file)
        asar.write(icon_to_repl, pngbytes)
        if backup:
            backup_file = "|".join(asar.keys)
            content = asar.old_content
            if content: # in case the icon doesn't exists anymore
                self.backup.file(backup_file, content)

        self.is_corrupted = not asar.success
