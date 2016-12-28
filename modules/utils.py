#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.6
Website : https://github.com/bil-elmoussaoui/Hardcode-Tray
Licence : The script is released under GPL, uses a modified script
     form Chromium project released under BSD license
This file is part of Hardcode-Tray.
Hardcode-Tray is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
TwoFactorAuth is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Hardcode-Tray. If not, see <http://www.gnu.org/licenses/>.
"""
from os import chown, getenv, makedirs, path, remove, symlink
from re import findall
from shutil import copyfile, move
from functools import reduce
from subprocess import PIPE, Popen, check_output
from modules.const import (USERHOME, CHMOD_IGNORE_LIST, USER_ID, GROUP_ID,
                           BACKUP_EXTENSION, SCRIPT_ERRORS)


def symlink_file(source, link_name):
    """Symlink a file, remove the dest file if already exists."""
    try:
        symlink(source, link_name)
    except FileExistsError:
        remove(link_name)
        symlink(source, link_name)
    except FileNotFoundError:
        pass


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


def mchown(directory):
    """
    Fix folder/file permissions.

    Args:
        directory (str): folder/file path
    """
    path_list = directory.split("/")
    dir_path = ""
    # Check if the file/folder is in the home directory
    if USERHOME in directory:
        for directory in path_list:
            dir_path += str(directory) + "/"
            # Be sure to not change / permissions
            if dir_path.replace("/", "") not in CHMOD_IGNORE_LIST:
                if path.isdir(dir_path):
                    chown(dir_path, USER_ID, GROUP_ID)
                else:
                    execute(["chmod", "0777", dir_path.rstrip("/")])


def create_dir(folder):
    """
    Create a directory and fix folder permissions.

    Args :
        folder (str): folder path
    """
    if not path.isdir(folder):
        makedirs(folder, exist_ok=True)
        mchown(folder)


def execute(command_list, verbose=True):
    """
    Run a command using "Popen".

    Args :
        command_list(list)
        verbose(bool)
    """
    cmd = Popen(command_list, stdout=PIPE, stderr=PIPE)
    output, error = cmd.communicate()
    if verbose and error and error not in SCRIPT_ERRORS:
        SCRIPT_ERRORS.append(error)
    return output


def backup(file_name):
    """
    Backup functions, enables reverting.

    Args:
        icon(str) : the original icon name
        revert(bool) : True: revert, False: only backup
    """
    back_file = file_name + BACKUP_EXTENSION
    if path.isfile(file_name):
        copy_file(file_name, back_file)


def revert(file_name):
    """
    Backup functions, enables reverting.

    Args:
        icon(str) : the original icon name
        revert(bool) : True: revert, False: only backup
    """
    back_file = file_name + BACKUP_EXTENSION
    if path.isfile(back_file):
        move(back_file, file_name)


def get_userhome():
    """Return home path."""
    userhome = check_output('sh -c "echo $HOME"', shell=True,
                            universal_newlines=True).strip()
    if userhome.lower() == "/root":
        userhome = "/home/" + getenv("SUDO_USER")
    return userhome


def get_iterated_icons(icons):
    """Used to avoid multiple icons names, like for telegram."""
    new_icons = []
    for icon in icons:
        search = findall(r"{\d+\-\d+}", icon)
        if len(search) == 1:
            values = search[0].strip("{").strip("}").split("-")
            minimum, maximum = int(values[0]), int(values[1])
            for i in range(minimum, maximum + 1):
                new_icons.append(icon.replace(search[0], str(i)))
        else:
            new_icons.append(icon)
    return new_icons

# Functions used in the electron script
def get_from_dict(data_dict, map_list):
    try:
        return reduce(lambda d, k: d[k], map_list, data_dict)
    except KeyError:
        return None


def set_in_dict(data_dict, map_list, value):
    get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value


def change_dict_vals(d, sizediff, offset):
    """Iterative funtion to account for the new size of the png bytearray."""
    if isinstance(d, dict):
        d2 = {k: change_dict_vals(v, sizediff, offset) for k, v in d.items()}
        if d2.get('offset') and int(d2.get('offset')) > offset:
            d2['offset'] = str(int(d2['offset']) + sizediff)
        return d2
    return d
