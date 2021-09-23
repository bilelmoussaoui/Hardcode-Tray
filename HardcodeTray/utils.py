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
from functools import reduce
from gettext import gettext as _
from os import makedirs, listdir, path, remove, symlink
from re import findall, match, sub
from shutil import copyfile
from subprocess import PIPE, Popen, call
from sys import stdout

from gi.repository import Gio

from HardcodeTray.const import KDE_CONFIG_FILE
from HardcodeTray.modules.log import Logger


def progress(count, count_max, time, app_name=""):
    """Used to draw a progress bar."""
    bar_len = 36
    space = 20
    filled_len = int(round(bar_len * count / float(count_max)))

    percents = round(100.0 * count / float(count_max), 1)
    progress_bar = '#' * filled_len + '.' * (bar_len - filled_len)

    stdout.write("\r{0!s}{1!s}".format(app_name,
                                       " " * (abs(len(app_name) - space))))
    stdout.write('[{0}] {1}/{2} {3}% {4:.2f}s\r'.format(progress_bar,
                                                        count, count_max,
                                                        percents, time))
    print("")
    stdout.flush()


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
    scaling_factor = None
    was_found = False

    try:
        with open(KDE_CONFIG_FILE, 'r') as kde_obj:
            data = kde_obj.readlines()

        for line in data:
            line = list(map(lambda x: x.strip(),
                            line.split("=")))

            if len(line) == 1:
                was_found = match(
                    r'\[Containments\]\[[0-9]+\]\[General\]', line[0])

            if len(line) > 1 and was_found and line[0].lower() == "iconsize":
                scaling_factor = int(line[1])
                break
        if scaling_factor:
            Logger.debug("Scaling Factor/KDE: {}".format(scaling_factor))

        return scaling_factor
    except (FileNotFoundError, KeyError) as kde_error:
        Logger.debug("Scaling Factor/KDE not detected.")
        Logger.error(kde_error)
    return None


def get_gnome_scaling_factor():
    """Return gnome scaling factor."""
    source = Gio.SettingsSchemaSource.get_default()
    if source.lookup("org.gnome.desktop.interface", True):
        gsettings = Gio.Settings.new("org.gnome.desktop.interface")
        scaling_factor = gsettings.get_uint('scaling-factor') + 1
        Logger.debug("Scaling Factor/GNOME: {}".format(scaling_factor))
        return scaling_factor
    else:
        Logger.debug("Scaling Factor/Gnome not detected.")
    return 1


def get_cinnamon_scaling_factor():
    """Return Cinnamon desktop scaling factor."""
    source = Gio.SettingsSchemaSource.get_default()
    if source.lookup("org.cinnamon.desktop.interface", True):
        gsettings = Gio.Settings.new("org.cinnamon.desktop.interface")
        scaling_factor = gsettings.get_uint('scaling-factor')
        if scaling_factor == 0:
            # Cinnamon does have an auto scaling feature which we can't use
            scaling_factor = 1
        Logger.debug("Scaling Factor/Cinnamon: {}".format(scaling_factor))
        return scaling_factor
    else:
        Logger.debug("Scaling Factor/Cinnamon not detected")
    return 1


def create_dir(directory):
    """
    Create a directory and fix folder permissions.

    Args :
        folder (str): folder path
    """
    if not path.exists(directory):
        Logger.debug("Creating directory: {}".format(directory))
        makedirs(directory, exist_ok=True)


def execute(command_list, verbose=True, shell=False, working_directory=None):
    """
    Run a command using "Popen".

    Args :
        command_list(list)
        verbose(bool)
    """
    Logger.debug("Executing command: {0}".format(" ".join(command_list)))
    if working_directory:
        cmd = Popen(command_list, stdout=PIPE, stderr=PIPE, shell=shell,
                    cwd=working_directory)
    else:
        cmd = Popen(command_list, stdout=PIPE, stderr=PIPE, shell=shell)

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


def get_pngbytes(icon):
    """Return the pngbytes of a svg/png icon."""
    from HardcodeTray.app import App
    icon_for_replace = icon.theme
    icon_extension = icon.theme_ext
    icon_size = icon.icon_size
    if icon_extension == 'svg':
        if icon_size != App.icon_size():
            png_bytes = App.svg().to_bin(icon_for_replace,
                                         App.icon_size())
        else:
            png_bytes = App.svg().to_bin(icon_for_replace)
    elif icon_extension == "png":
        with open(icon_for_replace, 'rb') as png_file:
            png_bytes = png_file.read()
    else:
        png_bytes = None
    return png_bytes


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
        ofval = d2.get('offset')
        if ofval and isinstance(ofval, str):
            ofval = int(ofval)
            if ofval > offset:
                d2['offset'] = str(ofval + sizediff)
        return d2
    return d


def replace_to_6hex(color):
    """Validate and replace 3hex colors to 6hex ones."""
    if match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color):
        if len(color) == 4:
            color = "#{0}{0}{1}{1}{2}{2}".format(color[1], color[2], color[3])
        return color
    else:
        exit(_("Invalid color {}").format(color))


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


def get_exact_folder(key, directory, condition):
    """
        Get subdirs and apply a condition on each until one is found.
    """
    dirs = directory.split(key)
    exact_directory = ""

    if path.isdir(dirs[0]):
        directories = listdir(dirs[0])
        for dir_ in directories:
            if condition(path.join(dirs[0], dir_, "")):
                exact_directory = dir_
                break

    if exact_directory:
        directory = directory.replace(key, exact_directory)

    return directory
