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
from os import makedirs, path, remove
from shutil import make_archive, rmtree
from tempfile import gettempdir
from zipfile import ZipFile

from HardcodeTray.modules.log import Logger
from HardcodeTray.modules.applications.helpers.extract import ExtractApplication


class ZipApplication(ExtractApplication):
    """Zip Application class."""

    def __init__(self, parser):
        """Init method."""
        ExtractApplication.__init__(self, parser)

        self.tmp_path = path.join(gettempdir(), "_{}".format(self.name))
        self.tmp_data = path.join(self.tmp_path, self.zip_path)

    def extract(self, icon_path):
        """Extract the zip file in /tmp directory."""
        if path.exists(self.tmp_path):
            rmtree(self.tmp_path)

        makedirs(self.tmp_path, exist_ok=True)

        Logger.debug("Zip Application: Extracting of {} started".format(self.binary))

        with ZipFile(path.join(str(icon_path), self.binary)) as zip_object:
            zip_object.extractall(self.tmp_path)

        Logger.debug("Zip Application: Extracting is done.")

    def pack(self, icon_path):
        """Recreate the zip file from the tmp directory."""
        zip_file = path.join(str(icon_path), self.binary)

        if path.isfile(zip_file):
            Logger.debug("Zip Application: Removing old binary file {}".format(zip_file))
            remove(zip_file)

        make_archive(zip_file.replace(".zip", ""), 'zip', self.tmp_path)
        Logger.debug("Zip Application: Creating a new zip archive.")

        if path.exists(self.tmp_path):
            rmtree(self.tmp_path)
