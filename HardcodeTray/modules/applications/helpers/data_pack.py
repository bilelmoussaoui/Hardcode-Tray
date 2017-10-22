"""
Support for formatting a data pack file.

Used for platform agnostic resource files.
Copyright (c) 2012 The Chromium Authors. All rights reserved.
Use of this source code is governed by a BSD-style license that can be
found in the LICENSE directory.
"""
from struct import pack, unpack

from HardcodeTray.modules.log import Logger


class DataPack:
    """Read and write .pak files."""
    HEADER = {
        # int32(version), int32(resource_count), int8(encoding)
        # 4 byte version number
        # 4 byte number of resources
        # 1 byte encoding
        4: {
            'length': 2 * 4 + 1,
            'fmt': '<IIB'
        },
        # int32(version), int8(encoding), 3 bytes padding,
        # int16(resource_count), int16(alias_count)
        # 4 bytes version number
        # 4 bytes encoding + padding
        # 2 bytes number of resources
        # 2 bytes number of aliases
        5: {
            'length': 4 + 1 + 3 + 2 * 2,
            'fmt': '<IIhh'
        }
    }

    def __init__(self, filename):
        """
        Args:
           filename: The path to the file.
        """
        self._filename = filename
        self._resources = {}
        self._version = 4
        # Header information
        self._header = None
        self._read()

    def haskey(self, key):
        """Verify if a key exists in the resources list."""
        return int(key) in self._resources.keys()

    def set_value(self, key, value):
        """Set a value in the resources list using a key."""
        try:
            self._resources[int(key)] = value
        except KeyError:
            Logger.warning("The key {0} dosen't seem to"
                           " be found on {1}".format(key, self._filename))

    def get_value(self, key):
        """Get the value of a specific key in the resources list."""
        try:
            return self._resources.get(int(key))
        except KeyError:
            Logger.warning("The key {0} dosen't seem to"
                           " be found on {1}".format(key, self._filename))
            return None

    def _read(self):
        """Read a data pack file and returns a dictionary."""
        with open(self._filename, 'rb') as file_object:
            data = file_object.read()
        original_data = data

        # Read the header.
        version = unpack('<i', data[:4])[0]
        _header = DataPack.HEADER[version]
        header = unpack(_header['fmt'], data[:_header['length']])
        self._version = version
        if version == 4:
            num_entries = header[1]
        elif version == 5:
            num_entries = header[2]
        self._header = header

        if num_entries != 0:
            # Read the index and data.
            data = data[_header['length']:]
            index_entry = 2 + 4  # Each entry is a uint16 and a uint32.
            for _ in range(num_entries):
                _id, offset = unpack('<HI', data[:index_entry])
                data = data[index_entry:]
                next_offset = unpack('<HI', data[:index_entry])[1]
                self._resources[_id] = original_data[offset:next_offset]

    def write(self):
        """Write a map of id=>data into output_file as a data pack."""
        ids = sorted(self._resources.keys())
        _header = DataPack.HEADER[self._version]
        ret = []
        # Write file header.
        ret.append(pack(_header['fmt'], *self._header))
        # Each entry is a uint16 + a uint32s. We have one extra entry for the last
        # item.
        index_length = (len(ids) + 1) * (2 + 4)

        # Write index.
        data_offset = _header['length'] + index_length
        for _id in ids:
            ret.append(pack('<HI', _id, data_offset))
            data_offset += len(self.get_value(_id))

        ret.append(pack('<HI', 0, data_offset))

        # Write data.
        for _id in ids:
            ret.append(self.get_value(_id))
        content = b''.join(ret)

        with open(self._filename, 'wb') as _file:
            _file.write(content)
