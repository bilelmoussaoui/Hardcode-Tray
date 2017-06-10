#!/usr/bin/python3
# pylint: disable=E0611
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
from __future__ import absolute_import

from json import dumps, loads
from struct import error as StructError
from struct import pack, unpack

from src.modules.log import Logger
from src.utils import (change_dict_vals, get_from_dict,
                       set_in_dict)

class AsarFile:
    """Write into ASAR files easily."""
    def __init__(self, asar_file):
        self._asar_file = asar_file
        self.success = True
        self._keys = []
        # hb for header bytes
        self._hb = [None, None, None]
        self._old_content = None
        self._get_header()

    @property
    def keys(self):
        """Keys to access to the file."""
        # See the write method
        return self._keys

    @property
    def old_content(self):
        """return the old content of the file."""
        return self._old_content

    def _get_header(self):
        asarfile = open(self._asar_file, 'rb')
        try:
            asarfile.seek(4)

            # header size is stored in byte 12:16

            self._hb[0] = unpack('I', asarfile.read(4))[0]
            self._hb[1] = unpack('I', asarfile.read(4))[0]
            self._hb[2] = unpack('I', asarfile.read(4))[0]
            self._zeros = (self._hb[1] - 4 - self._hb[2])

            header = asarfile.read(self._hb[2]).decode('utf-8')
            self._header = loads(header)
            self._offset = asarfile.tell() + self._zeros
            asarfile.close()
        except StructError:
            Logger.error(
                "Electron: Couldn't read asar file {}".format(self._asar_file))
            self.success = False

    def write(self, icon, pngbytes):
        """Write some bytes to a icon path."""
        self._keys = icon.split("/")

        fileinfo = get_from_dict(self._header, self._keys)
        # Make sure the icon to replace is found on the asar file
        # To avoid breaking the binary.
        # This is due to apps renaming/moving the icons around
        if  (not isinstance(fileinfo, dict)
             or "offset" not in fileinfo.keys()):
            return

        offset0 = int(fileinfo['offset'])
        offset = offset0 + self._offset
        size = int(fileinfo['size'])

        with open(self._asar_file, 'rb') as asarfile:
            asar = asarfile.read()

        set_in_dict(self._header, self._keys + ['size'], len(pngbytes))
        # Save the old binary content for backup
        # See electron.py
        self._old_content = asar[offset: offset + size]

        new_asar = pngbytes.join([asar[:offset],
                                  asar[offset + size:]])

        sizediff = len(pngbytes) - size
        # Replace the content on the header (as a dict)
        new_files = change_dict_vals(self._header, sizediff, offset0)
        new_header = dumps(new_files).encode('utf-8')
        header_length = len(new_header)

        first_byte = pack('I', header_length + (self._hb[0] - self._hb[2]))
        sec_byte = pack('I', header_length + (self._hb[1] - self._hb[2]))
        third_byte = pack('I', header_length)

        asar_content = b''.join([asar[:4], first_byte,
                                 sec_byte, third_byte, new_header,
                                 b'\x00' * self._zeros,
                                 new_asar[self._offset:]])

        asarfile = open(self._asar_file, 'wb')
        asarfile.write(asar_content)
        asarfile.close()
