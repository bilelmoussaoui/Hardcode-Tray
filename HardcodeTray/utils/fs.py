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
from os import makedirs, path, remove, symlink
from shutil import copyfile, rmtree

from HardcodeTray.modules.log import Logger

def symlink_file(source, link_name):
    """Symlink a file, remove the dest file if already exists."""
    try:
        symlink(source, link_name)
    except FileExistsError:
        remove(link_name)
        symlink_file(source, link_name)
    except FileNotFoundError:
        Logger.warning("File not found: {0}".format(source))


def copy_file(src, destination, overwrite=False):
    """
    Simple copy file function with the possibility to overwrite the file.

    Args :
        src(str) : source file
        dest(str) : destination folder
        overwrite(bool) : True to overwrite the file False by default
    """
    if overwrite:
        if path.isfile(destination):
            Logger.debug("Removing file: {}".format(destination))
            remove(destination)
        copyfile(src, destination)
    else:
        if not path.isfile(destination):
            copyfile(src, destination)


def get_extension(filename):
    """
    Return the file extension.

    Args:
        filename(str) : file name
    Returns
        str : file extension
    """
    return path.splitext(filename)[1].strip(".").lower()


def create_dir(directory):
    """
    Create a directory and fix folder permissions.

    Args :
        folder (str): folder path
    """
    if not path.exists(directory):
        Logger.debug("Creating directory: {}".format(directory))
        makedirs(directory, exist_ok=True)


def remove_dir(directory):
    if path.exists(directory):
        Logger.debug("Removing directory: {}".format(directory))
        rmtree(directory)
    return False
