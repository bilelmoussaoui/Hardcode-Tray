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

    def __init__(self, filename):
        """
        Args:
           filename: The path to the file.
        """
        self._filename = filename
        self._resources = {}
        self._aliases = {}
        self._version = 4
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
        # Read the header.
        version = unpack('<I', data[:4])[0]
        self._version = version
        if version == 4:
            resources_count, encoding = unpack('IB', data[4:0])
            alias_count = 0
            header_size = 9
        elif version == 5:
            encoding, resources_count, alias_count = unpack(
                'BxxxHH', data[4:12])
            header_size = 12

        def entry_at_index(idx):
            entry_size = 2 + 4
            offset = header_size + idx * entry_size
            return unpack('<HI', data[offset: offset + entry_size])

        prev_resource_id, prev_offset = entry_at_index(0)
        resources = {}
        # Read the resources
        for i in range(1, resources_count + 1):
            resource_id, offset = entry_at_index(i)
            resources[prev_resource_id] = data[prev_offset: offset]
            prev_resource_id, prev_offset = resource_id, offset
        # Read the entries
        id_table_size = (resources_count + 1) * (2 + 4)

        def alias_at_index(idx):
            alias_size = 2 + 2
            offset = header_size + id_table_size + idx * alias_size
            return unpack('<HH', data[offset: offset + alias_size])
        aliases = {}
        for i in range(alias_count):
            resource_id, index = alias_at_index(i)
            aliased_id = entry_at_index(index)[0]
            aliases[resource_id] = aliased_id
            resources[resource_id] = resources[aliased_id]
        self._resources = resources
        self._aliases = aliases

    def write(self):
        """Write a map of id=>data into output_file as a data pack."""
        ids = sorted(self._resources.keys())
        ret = []

        id_by_data = {self._resources[k]: k for k in reversed(ids)}
        alias_map = {k: id_by_data[v] for k, v in self._resources.items()
                     if id_by_data[v] != k}

        resource_count = len(self._resources) - len(alias_map)

        ret.append(pack('<IBxxxHH',
                        self._version,
                        0,
                        resource_count,
                        len(alias_map)
                        ))

        # Write index.
        HEADER_LENGTH = 4 + 4 + 2 + 2
        data_offset = HEADER_LENGTH + \
            (resource_count + 1) * 6 + len(alias_map) * 4

        index_by_id = {}
        deduped_data = []
        index = 0
        for resource_id in ids:
            if resource_id in alias_map:
                continue
            data = self._resources[resource_id]
            index_by_id[resource_id] = index
            ret.append(pack('<HI', resource_id, data_offset))
            data_offset += len(data)
            deduped_data.append(data)
            index += 1
        ret.append(pack('<HI', 0, data_offset))
        for resource_id in sorted(alias_map):
            index = index_by_id[alias_map[resource_id]]
            ret.append(pack('<HH', resource_id, index))

        ret.extend(deduped_data)

        with open(self._filename, 'wb') as _file:
            _file.write(b''.join(ret))
