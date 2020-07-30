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
from HardcodeTray.modules.applications.helpers.binary import BinaryApplication
from HardcodeTray.modules.log import Logger
from HardcodeTray.utils import get_pngbytes


class JavaScriptApplication(BinaryApplication):
    """JavaScript (Electron) application object."""

    def __init__(self, parser):
        """Use the parent class, Application, modify only the (re)install."""
        BinaryApplication.__init__(self, parser)

    def install_icon(self, icon, icon_path):
        """Install the icon."""
        icon.icon_size = App.icon_size()

        png_bytes = get_pngbytes(icon)

        if png_bytes:
            # Extract <binary_name> into /tmp/<binary_name>.unpacked
            extraction_path = "/tmp/%s.unpacked" % self.binary
            self.extract(extraction_path, icon_path)
            target_files = glob("%s/%s" % (extraction_path, self.file))
            # Create new base64 binary file
            base64_icon = b64encode(App.svg().to_bin(icon.theme, icon.icon_size, icon.icon_size))
            # Build new icon
            new_icon = "data:image/png;base64," + base64_icon.decode()
            # Replace the original icon with newly built one
            for file in target_files:
                with FileInput(file, inplace=True) as file:
                    for line in file:
                        print(line.replace(icon.original, new_icon), end='')
            # Pack /tmp/<binary_name>.unpacked back to default location
            self.pack(extraction_path, icon_path)
        else:
            Logger.error("Icon file was not found.")

    def extract(self, output_path, icon_path):
        """Extract binary file into output_path."""
        system("npx asar extract %s%s %s 2> /dev/null" % (icon_path, self.binary, output_path))

    def pack(self, input_path, icon_path):
        """Pack extracted binary file back to default location."""
        system("npx asar pack %s %s%s 2> /dev/null" % (input_path, icon_path, self.binary))

    def revert_icon(self, icon, icon_path):
        """Revert to the original icon."""
        # I don't know what is the best way to handle backup here.
        # Maybe backup whole app.asar file?
        Logger.error("Backup file of {0} was not found".format(self.name))
