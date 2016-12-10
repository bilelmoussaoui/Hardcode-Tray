#!/usr/bin/python3
"""
Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.5.2.1
Website : https://github.com/bil-elmoussaoui/Hardcode-Tray
Licence : The script is released under GPL, uses a modified script
        form Chromium project released under BSD license
"""

from argparse import ArgumentParser
from imp import load_source
from json import load
from os import (chown, environ, getenv, geteuid, listdir, makedirs, path,
                remove, symlink)
from re import findall
from shutil import copyfile, move, rmtree
from subprocess import PIPE, Popen, check_output
from sys import stdout

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk


# Force X11 instead of Wayland
environ['GDK_BACKEND'] = 'x11'

db_folder = "database/"
script_folder = "scripts/"
backup_extension = ".bak"
userhome = check_output('sh -c "echo $HOME"', shell=True,
                        universal_newlines=True).strip()
if userhome.lower() == "/root":
    userhome = "/home/" + getenv("SUDO_USER")
parser = ArgumentParser(prog="Hardcode-Tray")
absolute_path = path.split(path.abspath(__file__))[0] + "/"
theme = Gtk.IconTheme.get_default()
default_icon_size = 22
supported_icons_cnt = 0
chmod_ignore_list = ["", "home"]
fixed_apps = []
reverted_apps = []
script_errors = []

parser.add_argument("--size", "-s", help="use a different icon size instead "
                    "of the default one.",
                    type=int, choices=[16, 22, 24])
parser.add_argument("--theme", "-t",
                    help="use a different icon theme instead "
                    "of the default one.",
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
parser.add_argument("--force-inkscape", "-fs", action='store_true',
                    help="Use inkscape by default instead of Cairo")
args = parser.parse_args()

try:
    svgtopng = load_source(
        "svgtopng", "%s/database/scripts/svgtopng.py" % absolute_path)
    if args.force_inkscape:
        svgtopng.set_default_conversion_tool("inkscape")
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
    path_list = directory.split("/")
    dir_path = ""
    # Check if the file/folder is in the home directory
    if userhome in directory:
        for directory in path_list:
            dir_path += str(directory) + "/"
            # Be sure to not change / permissions
            if dir_path.replace("/", "") not in chmod_ignore_list:
                if path.isdir(dir_path):
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


def replace_vars_path(path, exec_path_script):
    """
        Replace some variables like {userhome} in application/icons path
        Args:
            path(str) : the application/icons path
            exec_path_script(bool/str): False or the name of the script
                            to be executed. Used in some cases like Dropbox
    """
    path = path.replace("{userhome}", userhome)
    if exec_path_script:
        sfile = absolute_path + db_folder + script_folder + exec_path_script
        path = execute([sfile, path], verbose=True).decode("utf-8").strip()
    return path


def check_paths(data):
    """
        Check if the app_path exists to detect if the application is installed
        Also check if the icons path exists, and force creating needed folders.
        See the json key "force_create_folder"
    """
    new_app_path = []
    for app_path in data["app_path"]:
        app_path = replace_vars_path(app_path, data["exec_path_script"])
        if path.isdir(app_path) or path.isfile(app_path):
            new_app_path.append(app_path)
    data["app_path"] = new_app_path
    if not len(data["app_path"]) == 0:
        new_icons_path = []
        for icon_path in data["icons_path"]:
            icon_path = replace_vars_path(icon_path, data["exec_path_script"])
            if data["force_create_folder"]:
                create_dir(icon_path)
            if path.isdir(icon_path):
                new_icons_path.append(icon_path)
        data["icons_path"] = new_icons_path
    return data


def get_supported_apps(fix_only, custom_path=""):
    """
        Gets a list of dict, a dict for each supported application
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
                data = load(data_file)
                data = check_paths(data)
                be_added = len(data["app_path"]) > 0
                if custom_path:
                    if len(database_files) == 1 and path.exists(custom_path):
                        data["app_path"].append(custom_path)
                if be_added:
                    if isinstance(data["icons"], list):
                        data["icons"] = get_iterated_icons(data["icons"])
                    data["icons"], dont_install = get_app_icons(data)
                    if not dont_install:
                        supported_apps.append(data)
    return supported_apps


def get_icon_size(icon):
    """
        Get the icon size, with hidpi support (depends on the icon name)
        @Args: (list) icon
    """
    icon_size = default_icon_size
    icon_name = icon.split("@")
    if len(icon_name) > 1:
        multiple = int(icon_name[1].split("x")[0])
        if multiple and multiple != 0:
            icon_size *= multiple
    return icon_size


def get_iterated_icons(icons):
    """
        Used to avoid multiple icons names, like for telegram
        See telegram.json
    """
    new_icons = []
    for icon in icons:
        search = findall("{\d+\-\d+}", icon)
        if len(search) == 1:
            values = search[0].strip("{").strip("}").split("-")
            minimum, maximum = int(values[0]), int(values[1])
            for i in range(minimum, maximum + 1):
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
    global supported_icons_cnt
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
            supported_icons_cnt += 1

    dont_install = not len(supported_icons) > 0
    return (supported_icons, dont_install)


def progress(count, count_max, app_name):
    """
        Used to draw a progress bar
    """
    bar_len = 40
    space = 25
    filled_len = int(round(bar_len * count / float(count_max)))

    percents = round(100.0 * count / float(count_max), 1)
    bar = '#' * filled_len + '.' * (bar_len - filled_len)

    stdout.write("\r%s%s" % (app_name, " " * (abs(len(app_name) - space))))
    stdout.write('[%s] %i/%i %s%s\r' %
                 (bar, count, count_max, percents, '%'))
    print("")
    stdout.flush()


def symlink_file(source, link_name):
    """
        Symlink a file, remove the dest file if already exists
    """
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
    if not revert:
        if path.isfile(icon):
            copy_file(icon, back_file)
    if revert:
        if path.isfile(back_file):
            move(back_file, icon)


def reinstall(fix_only, custom_path):
    """
        Reverts to the original icons
    """
    apps = get_supported_apps(fix_only, custom_path)
    cnt = 0
    reverted_cnt = sum(len(app["icons"]) for app in apps)
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
                    elif app["is_script"]:
                        binary = app["binary"]
                        backup(icon_path + binary, revert=True)
                    else:
                        if not app["backup_ignore"]:
                            backup(icon_path +
                                   icon["original"], revert=True)
                            if "symlinks" in icon.keys():
                                for symlink_icon in icon["symlinks"]:
                                    symlink_icon = icon_path + symlink_icon
                                    if path.exists(symlink_icon):
                                        remove(symlink_icon)
                cnt += 1
            if app_name not in reverted_apps:
                progress(cnt, reverted_cnt, app_name)
                reverted_apps.append(app_name)


def install(fix_only, custom_path):
    """
        Installs the new supported icons
    """
    apps = get_supported_apps(fix_only, custom_path)
    if len(apps) != 0:
        cnt = 0
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
            for step_count, icon in enumerate(app_icons):
                if step_count == 0:
                    step = 0
                elif step_count == len(app_icons) -1:
                    step = -1
                else:
                    step = 1
                base_icon = icon["original"]
                ext_orig = icon["orig_ext"]
                fname = icon["theme"]
                ext_theme = icon["theme_ext"]
                for icon_path in icons_path:
                    if app["is_qt"]:
                        if svgtopng.is_svg_enabled():
                            output_icon = icon_path + base_icon
                            svgtopng.convert_svg2png(fname, output_icon)
                            mchown(output_icon)
                    elif app["is_script"]:
                        binary = app["binary"]
                        if path.exists(icon_path + binary):
                            backup(icon_path + binary)
                            script_file = absolute_path + db_folder + \
                                script_folder + app["script"]
                            cmd = [script_file, fname, base_icon,
                                   icon_path, binary, str(step)]
                            execute(cmd)
                    else:
                        output_icon = icon_path + base_icon
                        if not app["backup_ignore"]:
                            backup(output_icon)
                        if ext_theme == ext_orig:
                            symlink_file(fname, output_icon)
                        elif ext_theme == "svg" and ext_orig == "png":
                            if svgtopng.is_svg_enabled():
                                try:  # Convert the svg file to a png one
                                    if icon["icon_size"] != default_icon_size:
                                        svgtopng.convert_svg2png(
                                            fname, output_icon,
                                            icon["icon_size"])
                                    else:
                                        svgtopng.convert_svg2png(
                                            fname, output_icon)
                                    mchown(output_icon)
                                    if "symlinks" in icon.keys():
                                        for symlink_icon in icon["symlinks"]:
                                            symlink_icon = icon_path + symlink_icon
                                            symlink_file(output_icon, symlink_icon)
                                except Exception as e:
                                    print(e)
                cnt += 1
            if app_name not in fixed_apps:
                fixed_apps.append(app_name)
                progress(cnt, supported_icons_cnt, app_name)

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
    except KeyboardInterrupt:
        exit("")

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
print("\nDone, Thank you for using the Hardcode-Tray fixer!")
