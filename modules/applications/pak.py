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
from os import path
from imp import load_source
from modules.applications.application import Application

absolute_path = path.split(path.abspath(__file__))[0] + "/../"
data_pack = load_source('data_pack', absolute_path + 'data_pack.py')


class PakApplication(Application):
    """Pak Application class, based on data_pak file."""

    def __init__(self, application_data, svgtopng):
        Application.__init__(self, application_data, svgtopng)

    def reinstall(self):
        """Reinstall the old icons."""
        for icon_path in self.get_icons_path():
            self.revert_binary(icon_path)

    def install(self):
        """Install the application icons."""
        self.install_symlinks()
        for icon_path in self.get_icons_path():
            self.backup_binary(icon_path)
            for icon in self.get_icons():
                self.install_icon(icon, icon_path)

    def install_icon(self, icon, icon_path):
        """Install the icon."""
        filename = icon_path + self.app.data["binary"]
        icon_to_repl = icon["original"]
        icon_for_repl = icon["theme"]
        icon_extension = icon["orig_ext"]
        if self.svgtopng.is_svg_enabled:
            if icon_extension == '.svg':
                pngbytes = self.svgtopng.to_bin(icon_for_repl)
            else:
                with open(icon_for_repl, 'rb') as pngfile:
                    pngbytes = pngfile.read()

            _data_pack = data_pack.read_data_pack(filename)
            _data_pack.resources[int(icon_to_repl)] = pngbytes
            data_pack.write_data_pack(_data_pack.resources, filename, 0)
