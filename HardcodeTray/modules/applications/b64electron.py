"""
Fixes Hardcoded tray icons in Linux.

Author : Ivo Šmerek (ivo.smerek@gmail.com)
Contributors : Bilal Elmoussaoui, Alexey Varfolomeev
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
from base64 import b64encode
from glob import glob
from os import path, system
from fileinput import FileInput

from HardcodeTray.app import App
from HardcodeTray.modules.applications.electron import ElectronApplication
from HardcodeTray.modules.applications.helpers.asar import AsarFile
from HardcodeTray.modules.log import Logger
from HardcodeTray.utils import get_pngbytes


class B64ElectronApplication(ElectronApplication):
    """Electron application with Base64 hardcoded icons."""

    def __init__(self, parser):
        """Use the parent class, Application, modify only the (re)install."""
        ElectronApplication.__init__(self, parser)

    def install_icon(self, icon, icon_path):
        """Install the icon."""
        icon.icon_size = App.icon_size()

        png_bytes = get_pngbytes(icon)

        if png_bytes:
            # Read a target file
            asar = AsarFile(path.join(str(icon_path), self.binary))
            target = B64ElectronApplication.get_real_path(self.file)
            file_content = asar.read_file(target).decode()
            # Create new base64 binary file
            base64_icon = b64encode(App.svg().to_bin(icon.theme, icon.icon_size, icon.icon_size))
            # Build new icon
            new_icon = "data:image/png;base64," + base64_icon.decode()
            # Replace the original icon with newly built one
            file_content = file_content.replace(icon.original, new_icon)
            bytes = file_content.encode()
            self.set_icon(target, icon_path, bytes, True)
        else:
            Logger.error("Icon file was not found.")

    def revert_icon(self, icon, icon_path):
        """Revert to the original icon."""
        target = B64ElectronApplication.get_real_path(self.file)
        backup_file = "|".join(target.split("/"))

        bytes = self.get_backup_file(backup_file)
        if bytes:
            self.set_icon(target, icon_path, bytes)
        else:
            Logger.error("Backup file of {0} was not found".format(self.name))

    def set_icon(self, icon_to_replace, binary_path, png_bytes, backup=False):
        """Set the icon into the electron binary file."""
        binary_file = path.join(str(binary_path), self.binary)

        asar = AsarFile(binary_file)
        asar.write(icon_to_replace, png_bytes)
        backup_file = "|".join(asar.keys)
        # If script edits one file multiple times,
        # it has to backup only the first time.
        if backup and not self.backup._exists:
            content = asar.old_content
            if content:  # in case the icon doesn't exists anymore
                self.backup.file(backup_file, content)
                self.backup._exists = True

        self.is_corrupted = not asar.success
