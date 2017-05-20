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
from os import path
from imp import load_source
from .binary import BinaryApplication
from src.utils import get_pngbytes

absolute_path = path.split(path.abspath(__file__))[0]
data_pack_path = path.join(absolute_path, "pak", "data_pack.py")
data_pack = load_source('data_pack', data_pack_path)


class PakApplication(BinaryApplication):
    """Pak Application class, based on data_pak file."""

    def __init__(self, application_data):
        """Init method."""
        BinaryApplication.__init__(self, application_data)

    def install_icon(self, icon, icon_path):
        """Install the icon."""
        filename = icon_path + self.binary
        icon_to_repl = int(icon["original"])
        pngbytes = get_pngbytes(self.svgtopng, icon)
        if pngbytes:
            _data_pack = data_pack.read_data_pack(filename)
            _data_pack.resources[icon_to_repl] = pngbytes
            data_pack.write_data_pack(_data_pack.resources, filename, 0)
