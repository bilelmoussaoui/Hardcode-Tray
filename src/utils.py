#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.8
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
from functools import reduce
from os import chown, listdir, makedirs, path, remove, symlink
from re import findall, match, sub
from shutil import copyfile
from subprocess import PIPE, Popen, call
from sys import stdout

from gi.repository import Gio

from src.const import (CHMOD_IGNORE_LIST, GROUP_ID, KDE_CONFIG_FILE, USER_ID,
                       USERHOME)
from src.modules.log import Logger


def progress(count, count_max, time, app_name=""):
    """Used to draw a progress bar."""
    bar_len = 40
    space = 20
    time = round(time, 2)
    filled_len = int(round(bar_len * count / float(count_max)))

    percents = round(100.0 * count / float(count_max), 1)
    progress_bar = '#' * filled_len + '.' * (bar_len - filled_len)

    stdout.write("\r{0!s}{1!s}".format(
        app_name, " " * (abs(len(app_name) - space))))
    stdout.write('[{0}] {1}/{2} {3}% {4}s\r'.format(progress_bar,
                                                    count, count_max,
                                                    percents, time))
    print("")
    stdout.flush()


def symlink_file(source, link_name):
    """Symlink a file, remove the dest file if already exists."""
    try:
        symlink(source, link_name)
        mchown(link_name)
    except FileExistsError:
        remove(link_name)
        symlink_file(source, link_name)
    except FileNotFoundError:
        Logger.debug("File name {0} was not found".format(source))


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


def get_kde_scaling_factor():
    """Return the widgets scaling factor on KDE."""
    scaling_factor = 1
    was_found = False

    try:
        with open(KDE_CONFIG_FILE, 'r') as kde_obj:
            data = kde_obj.readlines()

        for line in data:
            line = list(map(lambda x: x.strip(),
                            line.strip().split("=")))

            if len(line) == 1:
                was_found = match(
                    r'\[Containments\]\[[0-9]+\]\[General\]', line[0])

            if len(line) > 1 and was_found:
                if line[0].lower() == "iconsize":
                    scaling_factor = int(line[1])
                    break
        return scaling_factor
    except (FileNotFoundError, KeyError) as kde_error:
        Logger.debug("KDE scaling factor not detected."
                     " Error : {0!s}".format(kde_error))
    return None


def get_scaling_factor(desktop_env):
    """Return the widgets scaling factor."""
    scaling_factor = 1

    # Scaling factor on GNOME desktop
    if desktop_env == "gnome":

        gsettings = Gio.Settings.new("org.gnome.desktop.interface")
        scaling_factor = gsettings.get_uint('scaling-factor') + 1

        Logger.debug("Scaling factor of Gnome interface"
                     " is set to {0}".format(scaling_factor))

    # Scaling factor on KDE Desktop
    elif desktop_env == "kde":
        scaling_factor = get_kde_scaling_factor()

        Logger.debug("Scaling factor was detected in the KDE configuration"
                     "with the value {0}".format(scaling_factor))

    return scaling_factor


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
        for dir_ in path_list:
            dir_path += str(dir_) + "/"
            # Be sure to not change / permissions
            if dir_path.replace("/", "") not in CHMOD_IGNORE_LIST:
                if path.isdir(dir_path):
                    chown(dir_path, USER_ID, GROUP_ID)
                else:
                    file_path = dir_path.rstrip("/")
                    if not path.islink(file_path):
                        execute(["chmod", "0777", file_path])


def create_dir(folder):
    """
    Create a directory and fix folder permissions.

    Args :
        folder (str): folder path
    """
    if not path.exists(folder):
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
        Logger.error(error.decode("utf-8").strip())
    return output


def is_installed(binary):
    """Check if a binary file exists/installed."""
    ink_flag = call(['which', binary], stdout=PIPE, stderr=PIPE)
    return bool(ink_flag == 0)


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
                theme_path = path.join(icon_path, theme, "")
                theme_index = "{0!s}index.theme".format(theme_path)
                if (path.exists(theme_path) and path.exists(theme_index)
                        and theme not in themes):
                    themes.append(theme)
        except FileNotFoundError:
            pass
    return themes


def get_pngbytes(icon):
    """Return the pngbytes of a svg/png icon."""
    from src.app import App
    icon_for_repl = icon.theme
    icon_extension = icon.theme_ext
    icon_size = icon.icon_size
    if icon_extension == 'svg':
        pngbytes = App.svg().to_bin(icon_for_repl, icon_size)
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


def replace_to_6hex(color):
    """Validate and replace 3hex colors to 6hex ones."""
    if match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color):
        if len(color) == 4:
            color = "#{0}{0}{1}{1}{2}{2}".format(color[1], color[2], color[3])
        return color
    else:
        exit("Invalid color {0}".format(color))


def replace_colors(file_name, colors):
    """Replace the colors in a file name."""
    if path.isfile(file_name):
        # Open SVG file
        with open(file_name, 'r') as file_:
            file_data = file_.read()

        # Replace colors
        for color in colors:
            to_replace = color[0]
            for_replace = color[1]
            file_data = sub(to_replace, for_replace, file_data)

        # Save new file content on a tmp file.
        with open(file_name, 'w') as _file:
            _file.write(file_data)
        _file.close()
