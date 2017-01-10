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

def get_subdirs(directory):
    """
        Returns a list of subdirectories, used in replace_dropbox_dir
        Args:
            directory (str): path of the directory
    """
    if path.isdir(directory):
        dirs = listdir(directory)
        dirs.sort()
        sub_dirs = []
        for sub_dir in dirs:
            if path.isdir(directory + sub_dir):
                sub_dirs.append(sub_dir)
        sub_dirs.sort()
        return sub_dirs
    else:
        return None

def replace_dropbox_dir(directory):
    """
        Corrects the hardcoded dropbox directory
        Args:
            directory(str): the default dropbox directory
    """
    dirs = directory.split("{dropbox}")
    sub_dirs = get_subdirs(dirs[0])
    if sub_dirs:
        if sub_dirs[0].split("-")[0] == "dropbox":
            return sub_dirs[0]
        else:
            logging.debug("Dropbox folder not found")
            return ""
    else:
        logging.debug("Dropbox folder not found")
        return ""

dropbox_path = argv[1]

dropbox_path = dropbox_path.replace(
    "{dropbox}", replace_dropbox_dir(dropbox_path))
print(dropbox_path)
