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
from struct import unpack, pack
from json import loads, dumps
from .binary import BinaryApplication
from src.utils import (get_from_dict, change_dict_vals,
                       set_in_dict, get_pngbytes)


class ElectronApplication(BinaryApplication):
    """Electron applicaton object."""

    def __init__(self, parser):
        """Use the parent class, Application, modify only the (re)install."""
        BinaryApplication.__init__(self, parser)

    def install_icon(self, icon, icon_path):
        """Install the icon."""
        filename = icon_path.append(self.binary)
        icon_to_repl = "files/{0!s}".format(
            "/files/".join(icon.original.split("/")))
        asarfile = open(filename, 'rb')
        asarfile.seek(4)

        # header size is stored in byte 12:16
        len1 = unpack('I', asarfile.read(4))[0]
        len2 = unpack('I', asarfile.read(4))[0]
        len3 = unpack('I', asarfile.read(4))[0]
        header_size = len3
        zeros_padding = (len2 - 4 - len3)

        header = asarfile.read(header_size).decode('utf-8')
        files = loads(header)
        originaloffset = asarfile.tell() + zeros_padding
        asarfile.close()

        keys = icon_to_repl.split('/')

        fileinfo = get_from_dict(files, keys)
        if isinstance(fileinfo, dict) and "offset" in fileinfo.keys():
            offset0 = int(fileinfo['offset'])
            offset = offset0 + originaloffset
            size = int(fileinfo['size'])

            with open(filename, 'rb') as asarfile:
                bytearr = asarfile.read()
            asarfile.close()

            pngbytes = get_pngbytes(icon)

            if pngbytes:
                set_in_dict(files, keys + ['size'], len(pngbytes))

                newbytearr = pngbytes.join(
                    [bytearr[:offset], bytearr[offset + size:]])

                sizediff = len(pngbytes) - size

                newfiles = change_dict_vals(files, sizediff, offset0)
                newheader = dumps(newfiles).encode('utf-8')
                newheaderlen = len(newheader)

                bytearr2 = b''.join([bytearr[:4],
                                     pack('I', newheaderlen + (len1 - len3)),
                                     pack('I', newheaderlen + (len2 - len3)),
                                     pack('I', newheaderlen), newheader,
                                     b'\x00' * zeros_padding,
                                     newbytearr[originaloffset:]])

                asarfile = open(filename, 'wb')
                asarfile.write(bytearr2)
                asarfile.close()
