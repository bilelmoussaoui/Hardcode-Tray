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
from os import path, remove
from shutil import make_archive, move, rmtree

from src.modules.applications.extract import ExtractApplication
from src.utils import execute


class NWJSApplication(ExtractApplication):
    """NWJS Application class."""

    def __init__(self, parser):
        """Init method."""
        ExtractApplication.__init__(self, parser)

        self.tmp_path = "/tmp/{0!s}_extracted/".format(self.name)
        self.tmp_data = path.join(self.tmp_path, self.nwjs_path)

    @property
    def nwjs_path(self):
        """Return the path of the icons in the zip file."""
        return self.parser.nwjs_path

    def extract(self, icon_path):
        """Extract the zip file in /tmp directory."""

        if path.exists(self.tmp_path):
            rmtree(self.tmp_path)

        execute(["unzip", icon_path + self.binary, "-d", self.tmp_path])

    def pack(self, icon_path):
        """Recreate the zip file from the tmp directory."""
        from src.app import App
        if App.config().get("nwjs") and path.exists(App.config().get("nwjs")):
            binary_file = "/tmp/{0}".format(self.binary)

            execute(["npm", "install"], True, True, self.tmp_path)

            make_archive(binary_file, "zip", self.tmp_path)

            move(binary_file + ".zip", binary_file + ".nw")

            local_binary_file = App.config().get("nwjs") + self.binary

            move(binary_file + ".nw", local_binary_file + ".nw")

            execute(["cat which nw " + self.binary + ".nw > " + self.binary],
                    True, True, App.config().get("nwjs"))

            remove(local_binary_file + ".nw")

            move(local_binary_file, icon_path + self.binary)
            execute(["chmod", "+x", icon_path + self.binary])

        rmtree(self.tmp_path)
