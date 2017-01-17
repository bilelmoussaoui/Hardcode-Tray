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
from gi import require_version
from os import chown, makedirs, path, remove, symlink, listdir
from re import findall
from shutil import copyfile, move, rmtree
from functools import reduce
from subprocess import PIPE, Popen, call
from modules.const import (USERHOME, CHMOD_IGNORE_LIST, USER_ID, GROUP_ID,
                           BACKUP_EXTENSION, BACKUP_FOLDER, BACKUP_FILE_FORMAT)
from time import strftime
import logging
require_version("Gtk", "3.0")
from gi.repository import Gtk


def symlink_file(source, link_name):
    """Symlink a file, remove the dest file if already exists."""
    try:
        symlink(source, link_name)
    except FileExistsError:
        remove(link_name)
        symlink(source, link_name)
    except FileNotFoundError:
        pass
    mchown(link_name)


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
    if verbose and error:
        logging.error(error)
    return output


def is_installed(binary):
    """Check if a binary file exists/installed."""
    ink_flag = call(['which', binary], stdout=PIPE, stderr=PIPE)
    return bool(ink_flag == 0)


def create_backup_dir(application_name):
    """Create a backup directory for an application (application_name)."""
    current_time_folder = strftime(BACKUP_FILE_FORMAT)
    back_dir = path.join(BACKUP_FOLDER, application_name,
                         current_time_folder, "")
    exists = True
    new_back_dir = back_dir
    i = 1
    while exists:
        if path.exists(new_back_dir):
            new_back_dir = back_dir + "_" + str(i)
        if not path.exists(new_back_dir):
            create_dir(new_back_dir)
            exists = False
        i += 1
    return new_back_dir


def backup(back_dir, file_name):
    """Backup functions."""
    back_file = path.join(back_dir, path.basename(
        file_name) + BACKUP_EXTENSION)
    if path.exists(file_name):
        logging.debug("Backup current file {0} to {1}".format(
            file_name, back_file))
        copy_file(file_name, back_file)
        mchown(back_file)
    if len(listdir(back_dir)) == 0:
        rmtree(back_dir)


def get_backup_folders(application_name):
    """Get a list of backup folders of a sepecific application."""
    return listdir(path.join(BACKUP_FOLDER, application_name))


def show_select_backup(application_name):
    """Show a select option for the backup of each application."""
    backup_folders = get_backup_folders(application_name)
    max_i = len(backup_folders)
    if max_i != 0:
        backup_folders.sort()
        i = 1
        for backup_folder in backup_folders:
            print("{0} ) {1}/{2} ".format(str(i),
                                          application_name, backup_folder))
            i += 1
        print("(Q)uit to not revert to any version")
        have_chosen = False
        stopped = False
        while not have_chosen and not stopped:
            try:
                selected_backup = input(
                    "Select a restore date : ").strip().lower()
                if selected_backup in ["q", "quit", "exit"]:
                    stopped = True
                selected_backup = int(selected_backup)
                if 1 <= selected_backup <= max_i:
                    have_chosen = True
                    backup_folder = backup_folders[selected_backup - 1]
                    return backup_folder
            except ValueError:
                pass
            except KeyboardInterrupt:
                exit()
        if stopped:
            logging.debug("The user stopped the reversion for "
                          "{0}".format(application_name))
        else:
            logging.debug("No backup folder found for the application "
                          "{0}".format(application_name))
    return None


def revert(application_name, selected_backup, file_name):
    """
    Backup functions, enables reverting.

    Args:
        icon(str) : the original icon name
        revert(bool) : True: revert, False: only backup
    """
    back_dir = path.join(BACKUP_FOLDER, application_name, selected_backup, "")
    if not path.exists(back_dir):
        back_file = path.join(back_dir, path.basename(
            file_name) + BACKUP_EXTENSION)
        if path.isfile(back_file):
            move(back_file, file_name)


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


def get_list_of_themes():
    """Return a list of installed icon themes."""
    paths = ["/usr/share/icons/",
             "{0!s}/.local/share/icons/".format(USERHOME)]
    themes = []
    for icon_path in paths:
        try:
            sub_dirs = listdir(icon_path)
            for theme in sub_dirs:
                theme_path = path.join(icon_path, theme) + "/"
                theme_index = "{0!s}index.theme".format(theme_path)
                if (path.exists(theme_path) and path.exists(theme_index)
                        and theme not in themes):
                    themes.append(theme)
        except FileNotFoundError:
            pass
    return themes


def create_icon_theme(theme_name, themes_list):
    """Return Gtk.IconTheme if it's a valid icon theme."""
    if theme_name in themes_list:
        theme = Gtk.IconTheme()
        theme.set_custom_theme(theme_name)
    else:
        exit("The theme {0!s} is not installed on your system.".format(
            theme_name))
    return theme


def get_pngbytes(svgtopng, icon):
    """Return the pngbytes of a svg/png icon."""
    icon_for_repl = icon["theme"]
    icon_extension = icon["theme_ext"]
    if svgtopng.is_svg_enabled and icon_extension == 'svg':
        pngbytes = svgtopng.to_bin(icon_for_repl)
    elif icon_extension == "png":
        with open(icon_for_repl, 'rb') as pngfile:
            pngbytes = pngfile.read()
        pngfile.close()
    else:
        pngbytes = None
    return pngbytes


# Functions used in the electron script
def get_from_dict(data_dict, map_list):
    """Get a value from a dictionnary following a map list."""
    try:
        return reduce(lambda d, k: d[k], map_list, data_dict)
    except KeyError:
        return None


def set_in_dict(data_dict, map_list, value):
    """Set a value in a dictionnary following a map list."""
    get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value


def change_dict_vals(d, sizediff, offset):
    """Iterative funtion to account for the new size of the png bytearray."""
    if isinstance(d, dict):
        d2 = {k: change_dict_vals(v, sizediff, offset) for k, v in d.items()}
        if d2.get('offset') and int(d2.get('offset')) > offset:
            d2['offset'] = str(int(d2['offset']) + sizediff)
        return d2
    return d


def change_colors_list(list_colours):
    """Transform a list of colours to a list of a sub-lists."""
    colours = []
    for color in list_colours:
        color = color.strip().split(" ")
        to_replace = color[0]
        for_replace = color[1]
        colours.append([to_replace, for_replace])
    return colours


def replace_colors(file_name, colors):
    """Replace the colors in a file name."""
    if path.isfile(file_name):
        with open(file_name, 'r') as _file:
            filedata = _file.read()
        _file.close()
        for color in colors:
            to_replace = color[0]
            for_replace = color[1]
            filedata = filedata.replace(to_replace, for_replace)

        with open(file_name, 'w') as _file:
            _file.write(filedata)
        _file.close()
