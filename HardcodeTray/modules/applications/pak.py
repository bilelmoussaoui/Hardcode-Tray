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

from HardcodeTray.modules.applications.helpers.binary import BinaryApplication
from HardcodeTray.modules.applications.helpers.data_pack import DataPack
from HardcodeTray.modules.log import Logger
from HardcodeTray.utils.icons import get_pngbytes


class PakApplication(BinaryApplication):
    """Pak Application class, based on data_pak file."""

    def __init__(self, parser):
        """Init method."""
        BinaryApplication.__init__(self, parser)

        self.binary_file = None
        self.pak = None

    def set_binary_file(self, binary_file):
        """Set pak file and create a new instance of it."""
        if binary_file != self.binary_file and path.exists(binary_file):
            self.binary_file = binary_file
            self.pak = DataPack(binary_file)

    def set_icon(self, icon, icon_path, pngbytes, backup=False):
        """Update the icon bytes with the new one."""
        self.set_binary_file(path.join(str(icon_path), self.binary))
        if self.pak:
            icon_name = icon.original
            if pngbytes and self.pak.haskey(icon_name):
                if backup:
                    self.backup.file(icon_name, self.pak.get_value(icon_name))

                self.pak.set_value(icon_name, pngbytes)
                self.pak.write()
            else:
                Logger.error("Couldn't find a PNG file.")
        else:
            Logger.warning(
                "The file {0} was not found".format(self.binary_file))

    def install_icon(self, icon, icon_path):
        """Install the new icon."""
        png_bytes = get_pngbytes(icon)
        self.set_icon(icon, icon_path, png_bytes, True)

    def revert_icon(self, icon, icon_path):
        """Revert to the original icon."""
        png_bytes = self.get_backup_file(icon.original)
        self.set_icon(icon, icon_path, png_bytes)
