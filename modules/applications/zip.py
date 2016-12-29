#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.6
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
from os import path, remove, makedirs
from zipfile import ZipFile
from modules.applications.application import Application
from shutil import make_archive, rmtree
from subprocess import PIPE, Popen


class ZipApplication(Application):
    """Pak Application class, based on data_pak file."""

    def __init__(self, application_data, svgtopng):
        """Init method."""
        Application.__init__(self, application_data, svgtopng)
        self.tmp_path = "/tmp/_{0!s}/".format(self.get_name())
        self.tmp_data = self.tmp_path + self.app.data["zip_path"]

    def reinstall(self):
        """Reinstall the old icons."""
        for icon_path in self.get_icons_path():
            self.revert_binary(icon_path)

    def extract(self, icon_path):
        """Extract the zip file in /tmp directory."""
        if path.exists(self.tmp_path):
            rmtree(self.tmp_path)
        makedirs(self.tmp_path, exist_ok=True)
        cmd = Popen(["chmod", "0777", self.tmp_path], stdout=PIPE, stderr=PIPE)
        cmd.communicate()
        with ZipFile(icon_path) as zf:
            zf.extractall(self.tmp_path)

    def pack(self, icon_path):
        """Recreate the zip file from the tmp directory."""
        zip_file = icon_path
        if path.isfile(zip_file):
            remove(zip_file)
        make_archive(zip_file.replace(".zip", ""), 'zip', self.tmp_path)
        rmtree(self.tmp_path)

    def install(self):
        """Install the application icons."""
        self.install_symlinks()
        for icon_path in self.get_icons_path():
            self.backup_binary(icon_path)
            self.extract(icon_path)
            for icon in self.get_icons():
                self.install_icon(icon, self.tmp_data)
            self.pack(icon_path)
