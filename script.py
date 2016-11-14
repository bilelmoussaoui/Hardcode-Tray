#!/usr/bin/python3
"""
Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.5
Website : https://github.com/bil-elmoussaoui/Hardcode-Tray
Licence : The script is released under GPL,
        uses some icons and a modified script form Chromium project
        released under BSD license
"""

from collections import OrderedDict
from csv import reader
from hashlib import md5
from imp import load_source
from os import (chown, environ, getenv, geteuid, listdir, makedirs,
                path, remove, symlink)
from shutil import copyfile, move, rmtree
from subprocess import PIPE, Popen, call, check_output
from sys import exit, stdout
from time import sleep
import argparse
import json
import re
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk

db_folder = "database/"
script_folder = "scripts/"
backup_extension = ".bak"
userhome = check_output('sh -c "echo $HOME"', universal_newlines=True,
                        shell=True).strip()
if userhome.lower() == "/root":
    userhome = "/home/" + getenv("SUDO_USER")
parser = argparse.ArgumentParser(prog="Hardcode-Tray")
absolute_path = path.split(path.abspath(__file__))[0] + "/"
theme = Gtk.IconTheme.get_default()
default_icon_size = 22
supported_icons_count = 0
chmod_ignore_list = ["", "home"]
fixed_icons = []
reverted_apps = []
script_errors = []
parser.add_argument("--size", "-s", help="use a different icon size instead "
                    "of the default one.",
                    type=int, choices=[16, 22, 24])
parser.add_argument("--theme", "-t",
                    help="use a different icon theme instead of the default one.",
                    type=str)
parser.add_argument("--only", "-o",
                    help="fix only one application or more, linked by a ','.\n"
                    "example : --only dropbox,telegram",
                    type=str)
parser.add_argument("--path", "-p",
                    help="use a different icon path for a single icon.",
                    type=str)
parser.add_argument("--update", "-u", action='store_true',
                    help="update Hardcode-Tray to the latest stable version.")
parser.add_argument("--update-git", "-ug", action='store_true',
                    help="update Hardcode-Tray to the latest git commit.")
parser.add_argument("--version", "-v", action='store_true',
                    help="print the version number of Hardcode-Tray.")
parser.add_argument("--apply", "-a", action='store_true',
                    help="fix hardcoded tray icons")
parser.add_argument("--revert", "-r", action='store_true',
                    help="revert fixed hardcoded tray icons")
args = parser.parse_args()

try:
    svgtopng = load_source(
        "svgtopng", "%s/database/scripts/svgtopng.py" % absolute_path)
except FileNotFoundError:
    exit("You need to clone the whole repository to use the script.")

try:
    data_pack = load_source(
        "data_pack", "%s/database/scripts/data_pack.py" % absolute_path)
except FileNotFoundError:
    exit("You need to clone the whole repository to use the script.")

if geteuid() != 0:
    exit("You need to have root privileges to run the script.\
        \nPlease try again, this time using 'sudo'. Exiting.")

if not (environ.get("DESKTOP_SESSION") or
        environ.get("XDG_CURRENT_DESKTOP")) and not args.size:
    exit("You need to run the script using 'sudo -E'.\nPlease try again")

if args.theme:
    theme_name = args.theme
    try:
        theme = Gtk.IconTheme()
        theme.set_custom_theme(theme_name)
    except Exception:
        exit("The choosen theme does not exists")
else:
    source = Gio.SettingsSchemaSource.get_default()
    if source.lookup("org.gnome.desktop.interface", True):
        gsettings = Gio.Settings.new("org.gnome.desktop.interface")
        theme_name = str(gsettings.get_value("icon-theme")).strip("'")
    else:
        gsettings = None


def detect_de():
    """
        Detects the desktop environment, used to choose the proper icons size
    """
    try:
        desktop_env = [environ.get("DESKTOP_SESSION").lower(
        ), environ.get("XDG_CURRENT_DESKTOP").lower()]
    except AttributeError:
        desktop_env = []
    if "pantheon" in desktop_env:
        return "pantheon"
    else:
        try:
            out = execute(["ls", "-la", "xprop -root _DT_SAVE_MODE"],
                          verbose=False)
            if " = \"xfce4\"" in out.decode("utf-8"):
                return "xfce"
            else:
                return "other"
        except (OSError, RuntimeError):
            return "other"


def mchown(directory):
    """
        Fix folder/file permissions
        Args:
            directory (str): folder/file path
    """
    global chmod_ignore_list
    path_list = directory.split("/")
    dir_path = "/"
    for directory in path_list:
        dir_path += str(directory) + "/"
        if dir_path.replace("/", "") not in chmod_ignore_list:
            if path.exists(dir_path):
                chown(dir_path, int(getenv("SUDO_UID")),
                      int(getenv("SUDO_GID")))
            elif path.isfile(dir_path.rstrip("/")):
                execute(["chmod", "0777", dir_path.rstrip("/")])


def create_dir(folder):
    """
        Create a directory and fix folder permissions
        Args :
            folder (str): folder path
    """
    if not path.isdir(folder):
        makedirs(folder, exist_ok=True)
        mchown(folder)


def execute(command_list, verbose=True):
    """
        Run a command using "Popen"
        Args :
            command_list(list)
            verbose(bool)
    """
    p = Popen(command_list, stdout=PIPE, stderr=PIPE)
    output, error = p.communicate()
    if verbose and error and error not in script_errors:
        script_errors.append(error)
    return output


def get_extension(filename):
    """
        returns the file extension
        Args:
            filename(str) : file name
        Returns
            str : file extension
    """
    return path.splitext(filename)[1].strip(".").lower()


def copy_file(src, destination, overwrite=False):
    """
        Simple copy file function with the possibility to overwrite the file
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


def check_paths(paths_list, exec_path_script):
    paths = []
    for i, icon_path in enumerate(paths_list):
        paths_list[i] = paths_list[i].replace("{userhome}", userhome)
        if exec_path_script:
            sfile = absolute_path + db_folder + \
                script_folder + exec_path_script
            paths_list[i] = execute([sfile, paths_list[i]], verbose=True).decode("utf-8").strip()
        if path.isdir(paths_list[i]) or path.isfile(paths_list[i]):
            paths.append(paths_list[i])
    return paths

def get_supported_apps(fix_only=[], custom_path=""):
    """
        Gets a list of supported applications: files in /database
    """
    database_files = listdir(absolute_path + db_folder)
    if len(fix_only) != 0:
        database_files = []
        for file in fix_only:
            if path.exists("%s%s.json" % (db_folder, file)):
                database_files.append("%s.json" % file)
    database_files.sort()
    supported_apps = []
    for file in database_files:
        file = "./%s%s" % (db_folder, file)
        be_added = True
        if path.isfile(file):
            with open(file) as data_file:
                data = json.load(data_file)
                data["icons_path"] = check_paths(data["icons_path"], data["exec_path_script"])
                data["app_path"] = check_paths(data["app_path"], data["exec_path_script"])
                if len(data["app_path"]) == 0:
                    be_added = False
                if custom_path and len(database_files) == 1 and path.exists(custom_path):
                    data["app_path"].append(custom_path)
                if be_added:
                    if isinstance(data["icons"], list):
                        data["icons"] = get_iterated_icons(data["icons"])
                    data["icons"], dont_install = get_app_icons(data)
                    if not dont_install:
                        if data["force_create_folder"]:
                            for icon_path in data["icons_path"]:
                                create_dir(icon_path)
                        supported_apps.append(data)
    return supported_apps


def get_icon_size(icon):
    """
        Get the icon size, with hidpi support (depends on the icon name)
        @Args: (list) icon
    """
    global default_icon_size
    icon_size = default_icon_size
    icon_name = icon.split("@")
    if len(icon_name) > 1:
        icon_size *= int(icon_name[1].split("x")[0])
    return icon_size


def get_iterated_icons(icons):
    new_icons = []
    for icon in icons:
        search = re.findall("{\d+\-\d+}", icon)
        if len(search) == 1:
            values = search[0].strip("{").strip("}").split("-")
            min, max = int(values[0]), int(values[1])
            for i in range(min, max + 1):
                new_icons.append(icon.replace(search[0], str(i)))
        else:
            new_icons.append(icon)
    return new_icons


def get_app_icons(data):
    """
        Gets a list of icons of each application
        Args:
            app_name(str): The application name
    """
    global supported_icons_count
    icons = data["icons"]
    supported_icons = []
    for icon in icons:
        if isinstance(icons, list):
            orig_icon = theme_icon = icon
        else:
            orig_icon = icons[icon]["original"]
            theme_icon = icons[icon]["theme"]
        ext_orig = get_extension(orig_icon)
        theme_icon = theme.lookup_icon(path.splitext(theme_icon)[
                                       0], default_icon_size, 0)
        if theme_icon:
            supported_icon = {}
            supported_icon["original"] = orig_icon
            supported_icon["theme"] = theme_icon.get_filename()
            supported_icon["theme_ext"] = get_extension(
                supported_icon["theme"])
            supported_icon["orig_ext"] = ext_orig
            supported_icon["icon_size"] = get_icon_size(orig_icon)

            if not isinstance(icons, list):
                if "symlinks" in icons[icon].keys():
                    supported_icon["symlinks"] = get_iterated_icons(
                        icons[icon]["symlinks"])

            supported_icons.append(supported_icon)
            supported_icons_count += 1

    dont_install = not len(supported_icons) > 0
    return (supported_icons, dont_install)


def progress(count, app_name):
    global supported_icons_count
    bar_len = 40
    space = 20
    filled_len = int(round(bar_len * count / float(supported_icons_count)))

    percents = round(100.0 * count / float(supported_icons_count), 1)
    bar = '#' * filled_len + '.' * (bar_len - filled_len)

    stdout.write("\r%s%s" % (app_name, " " * (abs(len(app_name) - space))))
    stdout.write('[%s] %i/%i %s%s\r' %
                 (bar, count, supported_icons_count, percents, '%'))
    stdout.flush()
    if count != supported_icons_count:
        stdout.write("\033[K")


def symlink_file(source, link_name):
    try:
        symlink(source, link_name)
    except FileExistsError:
        remove(link_name)
        symlink(source, link_name)
    except FileNotFoundError:
        pass


def backup(icon, revert=False):
    """
        Backup functions, enables reverting
        Args:
            icon(str) : the original icon name
            revert(bool) : True: revert, False: only backup
    """
    back_file = icon + backup_extension
    if path.isfile(icon):
        if not revert:
            copy_file(icon, back_file)
        elif revert:
            if path.isfile(back_file):
                move(back_file, icon)


def reinstall(fix_only, custom_path):
    """
        Reverts to the original icons
    """
    apps = get_supported_apps(fix_only, custom_path)
    if len(apps) != 0:
        for app in apps:
            app_path = app["app_path"]
            app_name = app["name"]
            app_icons = app["icons"]
            if "symlinks" in app.keys():
                for syml in app["symlinks"]:
                    for d in app_path:
                        dest = d + app["symlinks"][syml]["dest"]
                        backup(dest, revert=True)
            for icon in app_icons:
                icons_path = app["icons_path"]
                for icon_path in icons_path:
                    if app["is_qt"]:
                            if path.isdir(icon_path):
                                rmtree(icon_path)
                                print("%s -- reverted" % apps[app]["name"])
                    elif app["is_script"]:
                        binary = app["binary"]
                        if path.isfile(icon_path + binary):
                            backup(icon_path + binary, revert=True)
                    else:
                        if not app["backup_ignore"]:
                                backup(icon_path +
                                       icon["original"], revert=True)
                                if "symlinks" in icon.keys():
                                    for symlink_icon in icon["symlinks"]:
                                        symlink_icon = icon_path + symlink_icon
                                        remove(symlink_icon)
            if app_name not in reverted_apps:
                print("%s -- reverted" % (app_name))
                reverted_apps.append(app_name)


def install(fix_only, custom_path):
    """
        Installs the new supported icons
    """
    apps = get_supported_apps(fix_only, custom_path)
    if len(apps) != 0:
        counter = 0
        for app in apps:
            app_path = app["app_path"]
            app_name = app["name"]
            app_icons = app["icons"]
            icons_path = app["icons_path"]
            if "symlinks" in app.keys():
                for syml in app["symlinks"]:
                    for d in app_path:
                        root = app["symlinks"][syml]["root"]
                        dest = d + app["symlinks"][syml]["dest"]
                        backup(dest)
                        symlink_file(root, dest)
            for icon in app_icons:
                fixed = False
                base_icon = icon["original"]
                ext_orig = icon["orig_ext"]
                fname = icon["theme"]
                fbase = path.splitext(path.basename(fname))[0]
                ext_theme = icon["theme_ext"]
                for icon_path in icons_path:
                    if app["is_qt"]:
                        if svgtopng.is_svg_enabled():
                            output_icon = icon_path + base_icon
                            svgtopng.convert_svg2png(fname, output_icon)
                            mchown(output_icon)
                            if "symlinks" in icon.keys():
                                for symlink_icon in icon["symlinks"]:
                                    symlink_icon = icon_path + symlink_icon
                                    symlink_file(output_icon, symlink_icon)
                        fixed = True
                    elif app["is_script"]:
                        binary = app["binary"]
                        if path.exists(icon_path + binary):
                            backup(icon_path + binary)
                            script_file = absolute_path + db_folder + \
                                script_folder + app["script"]
                            execute(
                                [script_file, fname, base_icon, icon_path, binary])
                        fixed = True
                    else:
                        output_icon = icon_path + base_icon
                        if not app["backup_ignore"]:
                            backup(output_icon)
                        if ext_theme == ext_orig:
                            symlink_file(fname, output_icon)
                            fixed = True
                        elif ext_theme == "svg" and ext_orig == "png":
                            if svgtopng.is_svg_enabled():
                                try:  # Convert the svg file to a png one
                                    if icon["icon_size"] != default_icon_size:
                                        svgtopng.convert_svg2png(
                                            fname, output_icon, icon["icon_size"])
                                    else:
                                        svgtopng.convert_svg2png(
                                            fname, output_icon)
                                    mchown(output_icon)
                                    fixed = True
                                except Exception as e:
                                    print(e)
                                if "symlinks" in icon.keys():
                                    for symlink_icon in icon["symlinks"]:
                                        symlink_icon = icon_path + symlink_icon
                                        symlink_file(output_icon, symlink_icon)
                if fixed:
                    counter += 1
                    if not (fbase in fixed_icons) or counter == supported_icons_count:
                        progress(counter, app_name)
                        fixed_icons.append(fbase)
    else:
        exit("No apps to fix! Please report on GitHub if this is not the case")
if args.size:
    default_icon_size = args.size
else:
    if detect_de() in ("pantheon", "xfce"):
        default_icon_size = 24
choice = None
fix_only = args.only.lower().strip().split(",") if args.only else []

if args.path and fix_only and len(fix_only) == 1:
    icon_path = args.path
else:
    icon_path = None
if args.apply:
    choice = 1
if args.revert:
    choice = 2
print("Welcome to the tray icons hardcoder fixer!")
print("Your indicator icon size is : %s" % default_icon_size)
if args.theme or gsettings:
    print("Your current icon theme is : %s" % theme_name)
print("Svg to png functions are : ", end="")
print("Enabled" if svgtopng.is_svg_enabled() else "Disabled")
print("Applications will be fixed : ", end="")
print(",".join(fix_only) if fix_only else "All")

if not choice:
    print("1 - Apply")
    print("2 - Revert")
    try:
        choice = int(input("Please choose: "))
        if choice not in [1, 2]:
            exit("Please try again")
    except ValueError:
        exit("Please choose a valid value!")

if choice == 1:
    print("Applying now..\n")
    install(fix_only, icon_path)
elif choice == 2:
    print("Reverting now..\n")
    reinstall(fix_only, icon_path)

if len(script_errors) != 0:
    for err in script_errors:
        err = err.decode("utf-8")
        err = "\n".join(["\t" + e for e in err.split("\n")])
        print("fixing failed with error:\n%s" % err)
print("\nDone , Thank you for using the Hardcode-Tray fixer!")
