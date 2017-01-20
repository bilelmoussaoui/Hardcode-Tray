#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.6.5
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

import logging

from os import listdir, path
from sys import argv


def replace_hangouts_version_dir(directory):
    """
    Correct the hardcoded dropbox directory.

    Args:
        directory(str): the default dropbox directory
    """
    dirs = directory.split("{hangouts_version}")
    hangouts_folder = ""
    if path.isdir(dirs[0]):
        directories = listdir(dirs[0])
        for _dir in directories:
            if path.isdir(path.join(path.join(dirs[0]), _dir, "")):
                hangouts_folder = _dir
                break
        if hangouts_folder:
            return directory.replace("{hangouts_version}", hangouts_folder)
        else:
            logging.debug("Hangouts folder not found")
            return directory
    else:
        logging.debug("Hangouts folder not found")
        return directory


hangouts_path = argv[1]
hangouts_path = replace_hangouts_version_dir(hangouts_path)
print(hangouts_path)

