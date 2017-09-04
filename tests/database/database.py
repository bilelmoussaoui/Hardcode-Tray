#!/usr/bin/env python3
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
import json
from glob import glob
from os import path

from jsonschema import validate, ValidationError

DB_FOLDER = path.join(path.dirname(path.abspath(__file__)),
                      "../../data/database")
DB_FILES = sorted(glob("{}/*.json".format(DB_FOLDER)))
SCHEMA_FILE = path.join(path.dirname(path.abspath(__file__)), 'schema.json')

with open(SCHEMA_FILE, 'r') as schema_obj:
    SCHEMA = json.load(schema_obj)

has_errors = False
for data_file in DB_FILES:
    filename = path.basename(data_file)
    with open(data_file, 'r') as file_obj:
        try:
            validate(json.load(file_obj), SCHEMA)
        except (ValidationError, json.decoder.JSONDecodeError) as error:
            has_errors = True
            print("\033[91m File invalid: {}\033[0m".format(filename))
            print("\033[91m {}\033[0m".format(error))
        else:
            print("\033[92m File Valid: {}\033[0m".format(filename))
exit(int(has_errors))
