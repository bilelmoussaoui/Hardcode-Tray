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
from struct import unpack, pack, error as StructError
from json import loads, dumps
from src.utils import (get_from_dict, change_dict_vals,
                       set_in_dict, get_pngbytes)
from src.modules.applications.binary import BinaryApplication
from src.modules.log import Logger


class ElectronApplication(BinaryApplication):
    """Electron applicaton object."""

    def __init__(self, parser):
        """Use the parent class, Application, modify only the (re)install."""
        BinaryApplication.__init__(self, parser)

    def install_icon(self, icon, icon_path):
        """Install the icon."""
        pngbytes = get_pngbytes(icon)
        if pngbytes:
            self.set_icon(icon.original, icon_path, pngbytes, True)
        else:
            Logger.error("PNG file was not found.")

    @staticmethod
    def get_real_path(icon_name, delimiter="/"):
        """Get real path of an icon name inside the asar file."""
        return "files/{0}".format(
            "/files/".join(icon_name.split(delimiter)))

    def revert_icon(self, icon, icon_path):
        """Revert to the original icon."""
        backup_file = "|".join(ElectronApplication.get_real_path(icon.original).split("/"))
        pngbytes = self.get_backup_file(backup_file)
        if pngbytes:
            self.set_icon(icon.original, icon_path, pngbytes)
        else:
            Logger.error("Backup file of {0} was not found".format(self.name))

    def set_icon(self, icon_to_repl, binary_path, pngbytes, backup=False):
        """Set the icon into the electron binary file."""
        icon_to_repl = ElectronApplication.get_real_path(icon_to_repl)
        binary_file = binary_path.append(self.binary)

        asarfile = open(binary_file, 'rb')
        try:
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

            keys = icon_to_repl.split("/")

            fileinfo = get_from_dict(files, keys)
            if isinstance(fileinfo, dict) and "offset" in fileinfo.keys():
                offset0 = int(fileinfo['offset'])
                offset = offset0 + originaloffset
                size = int(fileinfo['size'])

                with open(binary_file, 'rb') as asarfile:
                    bytearr = asarfile.read()

                if pngbytes:
                    set_in_dict(files, keys + ['size'], len(pngbytes))

                    if backup:
                        backup_file = "|".join(keys)
                        self.backup.file(backup_file, bytearr[offset:offset+size])

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

                    asarfile = open(binary_file, 'wb')
                    asarfile.write(bytearr2)
                    asarfile.close()
        except StructError:
            Logger.error(
                "The asar file of {0} seems to be corrupted".format(self.name))
            self.is_corrupted = True
