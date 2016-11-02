#!/usr/bin/python3
"""
Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.2
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
from sys import exit
import argparse
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk

db_folder = "database/"
script_folder = "scripts/"
db_file = "db.csv"
backup_extension = ".bak"
userhome = check_output('sh -c "echo $HOME"', universal_newlines=True,
                        shell=True).strip()
if userhome.lower() == "/root":
    userhome = "/home/" + getenv("SUDO_USER")
parser = argparse.ArgumentParser(prog="Hardcode-Tray")
absolute_path = path.split(path.abspath(__file__))[0] + "/"
sni_qt_folder = userhome + "/.local/share/sni-qt/icons/"
images_folder = absolute_path + db_folder + "images/"
qt_script = "qt-tray"
theme = Gtk.IconTheme.get_default()
default_icon_size = 22
backup_ignore_list = ["hexchat"]
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
    if "pantheon" in [environ.get("DESKTOP_SESSION").lower(),
                      environ.get("XDG_CURRENT_DESKTOP").lower()]:
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
                chown(dir_path, int(getenv("SUDO_UID")), int(getenv("SUDO_GID")))
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


def get_correct_chrome_icons(apps_infos,
                             icons_dir="chromium"):
    """
        Returns the correct chrome indicator icons name in the pak file
        Args:
            apps_infos(list): Contains the information's in the database file
            icons_dir(str): Folder name that contains the default icons
    """
    images_dir = images_folder + icons_dir + "/"
    app_icons = apps_infos["icons"]
    app_icons.sort(key=lambda x: x[3])
    dicti = {}
    for i in range(len(app_icons)):
        k = 0
        icons = []
        while True:
            if k == 0:
                icon_name = images_dir + app_icons[i][1] + ".png"
            else:
                icon_name = images_dir + app_icons[i][1] + "%i.png" % (k)
            if path.isfile(icon_name):
                icons.append(open(icon_name, 'rb').read())
            else:
                break
            k = k + 1
        dicti[app_icons[i][0]] = icons
    pak_file = ''
    to_remove = []
    for i in range(len(app_icons)):
        pak = app_icons[i][3]
        if not (pak == pak_file):
            pak_file = pak
            if path.isfile(apps_infos["path"] + pak_file):
                datapak = data_pack.ReadDataPack(apps_infos["path"] + pak_file)
            else:
                to_remove.append(i)
                pak_file = ''
                continue
        if int(app_icons[i][4]) == 0:
            continue
        been_found = False
        for (resource_id, text) in datapak.resources.items():
            for icon in dicti[app_icons[i][0]]:
                if md5(text).hexdigest() == md5(icon).hexdigest():
                    app_icons[i][0] = resource_id
                    been_found = True
                    break
            if been_found:
                break
        if not been_found:
            to_remove.append(i)
    new_app_icons = []
    for i, val in enumerate(app_icons):
        if i not in to_remove:
            new_app_icons.append(app_icons[i])
    return (new_app_icons if len(new_app_icons) > 0 else None)


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
            return dirs[0] + sub_dirs[0] + dirs[1]
        else:
            return None
    else:
        return None


def create_hexchat_dir(apps_infos):
    """
        Create Hexchat icons directory located in $HOME/.config/hexchat/icons
        Args:
            apps_infos(list) : Hexchat informations in the database file
    """
    app_path = apps_infos[2].strip("/").split("/")
    icons_dir = app_path[len(app_path) - 1]
    del app_path[len(app_path) - 1]
    app_path = "/" + "/".join(app_path) + "/"
    if path.exists(app_path):
        create_dir(app_path + icons_dir + "/")


def get_supported_apps():
    """
        Gets a list of supported applications: files in /database
    """
    supported_apps = []
    for file in listdir(absolute_path + db_folder):
        if path.isfile(absolute_path + db_folder + file):
            supported_apps.append(file)
    return supported_apps

def get_icon_size(icon):
    """
        Get the icon size, with hidpi support (depends on the icon name)
        @Args: (list) icon
    """
    global default_icon_size
    icon_size = default_icon_size
    icon_name = icon[0].split("@")
    if len(icon_name) > 1:
        icon_size *= int(icon_name[1].split("x")[0])
    return icon_size

def get_apps_informations(fix_only, custom_path):
    """
        Reads the database file and returns a dictionary with all information
        Args:
            @fix_only (list): contains a list of applications
                                to be fixed/reverted
    """
    db = open(absolute_path + db_file)
    r = reader(db, skipinitialspace=True)
    next(r)
    apps = OrderedDict()
    ctr = 0
    fix_only = fix_only if fix_only else get_supported_apps()
    for app in r:
        if app[1] in fix_only:
            path_icon = custom_path if custom_path else app[2]
            path_icon = path_icon.replace("{userhome}", userhome).strip()
            if "{dropbox}" in path_icon:
                path_icon = replace_dropbox_dir(path_icon)
            if app[1] == "hexchat":
                create_hexchat_dir(app)
            if path_icon:
                if path.isdir(path_icon) or path.isfile(path_icon):
                    icons = get_app_icons(app[1])
                    if icons:
                        if app[1] in apps.keys():
                            app_name = app[1] + str(ctr)
                            ctr += 1
                        else:
                            app_name = app[1]
                            ctr = 0
                        apps[app_name] = OrderedDict()
                        apps[app_name]["name"] = app[0]
                        apps[app_name]["dbfile"] = app[1]
                        apps[app_name]["path"] = path_icon
                        apps[app_name]["icons"] = icons
                        if len(app) == 4 and app[3]:
                            apps[app_name]["sniqtprefix"] = app[3]
                    else:
                        continue
                else:
                    continue
            else:
                continue
    db.close()
    return apps


def get_app_icons(app_name):
    """
        Gets a list of icons of each application
        Args:
            app_name(str): The application name
    """
    if path.isfile(absolute_path + db_folder + app_name):
        f = open(absolute_path + db_folder + app_name)
        r = reader(f, skipinitialspace=True)
        icons = []
        for icon in r:
            if icon:
                if len(icon) != 1:
                    icons.append(icon)
                else:
                    icons.extend(icon)
        f.close()
        return icons
    else:
        print("The application " + app_name + " does not exist yet.\n\
            Please report this on GitHub")


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
            move(back_file, icon)


def reinstall(fix_only, custom_path):
    """
        Reverts to the original icons
    """
    sni_qt_reverted = False
    apps = get_apps_informations(fix_only, custom_path)
    if len(apps) != 0:
        for app in apps:
            app_icons = apps[app]["icons"]
            app_path = apps[app]["path"]
            app_db = apps[app]["dbfile"]
            revert_app = apps[app]["name"]
            for icon in app_icons:
                is_script = False
                if isinstance(icon, list):
                    icon = [item.strip() for item in icon]
                    if len(icon) > 2:
                        is_script = True
                        if icon[2] == qt_script:
                            if sni_qt_reverted:
                                continue
                            if path.exists(sni_qt_folder):
                                rmtree(sni_qt_folder)
                                print("Qt apps -- reverted")
                            sni_qt_reverted = True
                            continue
                    else:
                        revert_icon = icon[0]  # Hardcoded icon to be reverted
                else:
                    revert_icon = icon.strip()
                if not is_script:
                    if app_db == "hexchat":
                        if path.exists(app_path):
                            rmtree(app_path)
                    else:
                        try:
                            backup(app_path + revert_icon, revert=True)
                        except:
                            continue
                    if revert_app not in reverted_apps:
                        print("%s -- reverted" % (revert_app))
                        reverted_apps.append(revert_app)
                elif is_script:
                    try:
                        backup(app_path + icon[3], revert=True)
                    except:
                        continue
                    if revert_app not in reverted_apps:
                        print("%s -- reverted" % (revert_app))
                        reverted_apps.append(revert_app)


def install(fix_only, custom_path):
    """
        Installs the new supported icons
    """
    apps = get_apps_informations(fix_only, custom_path)
    if len(apps) != 0:
        for app in apps:
            app_path = apps[app]["path"]
            app_dbfile = apps[app]["dbfile"]
            app_name = apps[app]["name"]
            dont_install = False
            if app_dbfile in ("google-chrome", "chromium"):
                apps[app]["icons"] = get_correct_chrome_icons(apps[app])
                dont_install = not apps[app]["icons"]
            app_icons = apps[app]["icons"]
            icon_ctr = 1
            while (not dont_install) and (icon_ctr <= len(app_icons)):
                icon = app_icons[icon_ctr - 1]
                icon_size = get_icon_size(icon)
                is_script = False
                if isinstance(icon, list):
                    icon = [item.strip() for item in icon]
                    base_icon = path.splitext(icon[0])[0]
                    symlink_icon = path.splitext(icon[1])[0]
                    if len(icon) > 2:
                        is_script = True
                        sfile = absolute_path + db_folder + script_folder + icon[2]
                    if theme.lookup_icon(symlink_icon, icon_size, 0):
                        repl_icon = icon[1]
                        symlink_icon = icon[0]
                    else:
                        repl_icon = symlink_icon = icon[0]
                else:
                    symlink_icon = repl_icon = icon.strip()
                base_icon = path.splitext(repl_icon)[0]
                ext_orig = get_extension(symlink_icon)
                theme_icon = theme.lookup_icon(base_icon, icon_size, 0)
                if theme_icon:
                    fname = theme_icon.get_filename()
                    fbase = path.splitext(path.basename(fname))[0]
                    ext_theme = get_extension(fname)
                    # catching the case that theme is neither svg nor png
                    if ext_theme not in ("png", "svg"):
                        exit("Theme icons need to be svg or png files.\
                            \nOther formats are not supported yet")
                    if not is_script:
                        if symlink_icon:
                            output_icon = app_path + symlink_icon
                        else:
                            output_icon = app_path + repl_icon
                        if not(app_dbfile in backup_ignore_list):
                            backup(output_icon)
                        if ext_theme == ext_orig:
                            execute(["ln", "-sf", fname, output_icon])
                            if fbase not in fixed_icons:
                                print("%s -- fixed using %s" %
                                      (app_name, fbase))
                                fixed_icons.append(fbase)
                        elif ext_theme == "svg" and ext_orig == "png":
                            if svgtopng.is_svg_enabled():
                                try:  # Convert the svg file to a png one
                                    svgtopng.convert_svg2png(
                                        fname, output_icon)
                                    mchown(output_icon)
                                except:
                                    print("The svg file `%s` is invalid." %
                                          fname)
                                    continue
                                # to avoid identical messages
                                if not (fbase in fixed_icons):
                                    print("%s -- fixed using %s" %
                                          (app_name, fbase))
                                    fixed_icons.append(fbase)
                        elif ext_theme == "png" and ext_orig == "svg":
                            print("Theme icon is png and hardcoded icon is svg.\
                                \nThere is nothing we can do about that :(")
                            continue
                        else:
                            print("Hardcoded file has to be svg or png.\
                                \nOther formats are not supported yet")
                            continue
                    # Qt applications
                    else:
                        if svgtopng.is_svg_enabled():
                            if icon[2] == qt_script:
                                sni_qt_pre = apps[app].get("sniqtprefix", app)
                                sni_qt_path = sni_qt_folder + sni_qt_pre + "/"
                                if not path.exists(sni_qt_path):
                                    create_dir(sni_qt_path)
                                if len(icon) == 4:
                                    symlink_icon = sni_qt_path + symlink_icon
                                    original_icon = sni_qt_path + icon[3]
                                    try:
                                        remove(symlink_icon)
                                        symlink(original_icon, symlink_icon)
                                    except FileNotFoundError:
                                        symlink(original_icon, symlink_icon)
                                else:
                                    if path.isfile(sfile):
                                        execute([sfile, fname, symlink_icon,
                                                 sni_qt_path])
                                    else:
                                        script_errors.append("%s -- script "
                                                             "file does not"
                                                             "exists" % sfile)
                            else:
                                if path.isfile(sfile):
                                    backup(app_path + icon[3])
                                    execute([sfile, fname, symlink_icon,
                                             app_path, icon[3]])
                                else:
                                    script_errors.append("%s -- script file"
                                                         "does not exists" %
                                                         sfile)
                            # to avoid identical messages
                            if not (fbase in fixed_icons):
                                print("%s -- fixed using %s" %
                                      (app_name, fbase))
                                fixed_icons.append(fbase)
                icon_ctr += 1

    else:
        exit("No apps to fix! Please report on GitHub if this is not the case")

if args.size:
    default_icon_size = args.size
else:
    if detect_de() in ("pantheon", "xfce"):
        default_icon_size = 24
choice = None
fix_only = args.only.lower().strip().split(",") if args.only else None

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
        if choice not in [1,2]:
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
