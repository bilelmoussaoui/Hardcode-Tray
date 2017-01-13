#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.6.4
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
from os import path, listdir
from sys import argv
import logging


def replace_dropbox_dir(directory):
    """
    Correct the hardcoded dropbox directory.

    Args:
        directory(str): the default dropbox directory
    """
    dirs = directory.split("{dropbox}")
    if path.isdir(dirs[0]):
        directories = listdir(dirs[0])
        directories.sort()
        for _dir in directories:
            if path.isdir(_dir):
                splited_name = _dir.split("-").lower()
                if len(splited_name) > 1 and splited_name[0] == "dropbox":
                    return _dir
        logging.debug("Dropbox folder not found")
        return ""
    else:
        logging.debug("Dropbox folder not found")
        return ""


dropbox_path = argv[1]

dropbox_path = dropbox_path.replace(
    "{dropbox}", replace_dropbox_dir(dropbox_path))
print(dropbox_path)
