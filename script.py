#!/usr/bin/python3
'''
Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer , Joshua Fogg
Version : 1.2
Licence : The script is released under GPL,
        and uses some icons and a modified script form Chromium project released under BSD license
'''

from csv import reader
from gi.repository import Gtk, Gio
from os import environ, geteuid, getlogin, listdir, path, makedirs, chown, getenv, symlink, remove
from subprocess import Popen, PIPE, call
from sys import exit
from shutil import rmtree, copyfile, move
from hashlib import md5
from collections import OrderedDict
try:
    from cairosvg import svg2png
except ImportError:
    exit("You need to install python3-cairosvg to run this script.\nPlease install it and try again. Exiting.")

if geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

if not environ.get("DESKTOP_SESSION"):
    exit("Please run the script using 'sudo -E' to preserve environment variables")

db_file = "db.csv"
backup_extension = ".bak"
userhome = path.expanduser("~" + getlogin())
gsettings = Gio.Settings.new("org.gnome.desktop.interface")
db_folder = "database/"
script_folder = "scripts/"
aboslute_path = path.split(path.abspath(__file__))[0] + "/"
sni_qt_folder = userhome + "/.local/share/sni-qt/icons/"
images_folder = aboslute_path + db_folder + "images/"
theme = Gtk.IconTheme.get_default()
theme_name = str(gsettings.get_value("icon-theme")).strip("'")
qt_script = "qt-tray"
default_icon_size = 22
fixed_icons = []
reverted_apps = []
script_errors = []


def detect_de():
    """
        Detects the desktop environment, used to choose the proper icons size
    """
    if "pantheon" in [environ.get("DESKTOP_SESSION"), environ.get("XDG_CURRENT_DESKTOP").lower()]:
        return "pantheon"
    else:
        try:
            process = Popen(["ls", "-la", "xprop -root _DT_SAVE_MODE"], stdout=PIPE, stderr=PIPE)
            out = process.communicate()
            if " = \"xfce4\"" in out:
                return "xfce"
            else:
                return "other"
        except (OSError, RuntimeError):
            return "other"


def get_subdirs(directory):
    """
        Returns a list of subdirectories, used in replace_dropbox_dir
        @directory : String; path of the directory
    """
    if path.isdir(directory):
        dirs = listdir(directory)
        dirs.sort()
        sub_dirs = []
        for sub_dir in dirs:
            if path.isdir(directory + sub_dir):
                sub_dirs.append(sub_dir)
        return sub_dirs
    else:
        return None


def get_extension(filename):
    """
        returns the file extension
        @filename : String; file name
    """
    return path.splitext(filename)[1].strip(".").lower()


def copy_file(src, dest, overwrite=False):
    """
        Simple copy file function with the possibility to overwrite the file
        @src : String; source file
        @dest : String; destination folder
        @overwrite : Boolean; True to overwrite the file False by default
    """
    if overwrite:
        if path.isfile(dest):
            remove(dest)
        copyfile(src, dest)
    else:
        if not path.isfile(dest):
            copyfile(src, dest)


def filter_icon(list_icons, value):
    """
        Returns an integer:  the index of an icon in list
        @list_icons: list; list of icons with sublist
        @value: string; the name of icon that you're looking for
    """
    for i in range(len(list_icons)):
        for j in range(len(list_icons[i])):
            if list_icons[i][j] == value:
                return i


def get_correct_chrome_icons(apps_infos, chrome_pak_file="chrome_100_percent.pak"):
    """
        returns the correct chrome indicator icons name in the pak file
        @chrome_link: string; the chrome/chromium installation path
    """
    images_dir = images_folder + "chromium/"
    dirname = aboslute_path + db_folder + script_folder
    extracted = dirname + "extracted/"
    default_icons = ["google-chrome-notification",
                     "google-chrome-notification-disabled",
                     "google-chrome-no-notification",
                     "google-chrome-no-notification-disabled"]
    list_icons = {}
    if path.isfile(apps_infos[2] + chrome_pak_file):
        copyfile(apps_infos[2] + chrome_pak_file, dirname + chrome_pak_file)
        makedirs(path.dirname(extracted), exist_ok=True)
        r = Popen([dirname + "data_pack.py", dirname + chrome_pak_file], stdout=PIPE, stderr=PIPE)
        output, err = r.communicate()
        for file_name in listdir(extracted):
            icon = extracted + file_name
            if path.isfile(icon):
                for default_icon in default_icons:
                    default_content = open(images_dir + default_icon + ".png", "rb").read()
                    lookup_content = open(icon, "rb").read()
                    if md5(default_content).hexdigest() == md5(lookup_content).hexdigest():
                        list_icons[default_icon] = icon
            else:
                break
    if not list_icons or len(list_icons) < len(default_icons):
        if path.isdir(extracted):
            rmtree(extracted)
        if path.isfile(dirname + chrome_pak_file):
            remove(dirname + chrome_pak_file)
    return list_icons


def replace_dropbox_dir(directory):
    """
        Corrects the hardcoded dropbox directory
        @directory: string; the default dropbox directory
    """
    dirs = directory.split("{dropbox}")
    sub_dirs = get_subdirs(dirs[0])
    if sub_dirs:
        sub_dirs.sort()
        if sub_dirs[0].split("-")[0] == "dropbox":
            return dirs[0] + sub_dirs[0] + dirs[1]
        else:
            return None
    else:
        return None


def get_apps_informations(revert=False):
    """
        Reads the database file and returns a dictionary with all informations
    """
    db = open(db_file)
    r = reader(db, skipinitialspace=True)
    next(r)
    apps = OrderedDict()
    for app in r:
        dont_add = False
        app[2] = app[2].replace("{userhome}", userhome).strip()
        if "{dropbox}" in app[2]:
            app[2] = replace_dropbox_dir(app[2])
        if app[2]:
            if path.isdir(app[2]) or path.isfile(app[2]):
                icons = get_app_icons(app[1])
                if app[1] in ("google-chrome", "chromium") and not revert:
                        real_icons = get_correct_chrome_icons(app, icons[0][3])
                        if real_icons:
                            for new_icon in real_icons:
                                for old_icon in icons:
                                    if old_icon[1] == new_icon:
                                        icons[filter_icon(icons, new_icon)][0] = real_icons[new_icon]
                        else:
                            dont_add = True
                if icons and not dont_add:
                    apps[app[1]] = OrderedDict()
                    apps[app[1]]["name"] = app[0]
                    apps[app[1]]["dbfile"] = app[1]
                    apps[app[1]]["path"] = app[2]
                    apps[app[1]]["icons"] = icons
                    if len(app) == 4 and app[3]:
                        apps[app[1]]["sniqtprefix"] = app[3]
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
        gets a list of icons in /database/applicationname of each application
        @app_name: string; the application name
    """
    if path.isfile(db_folder + app_name):
        f = open(db_folder + app_name)
        r = reader(f, skipinitialspace=True)
        icons = []
        for icon in r:
            if icon != "":
                if len(icon) != 1:
                    icons.append(icon)
                else:
                    icons.extend(icon)
        f.close()
        icons.sort()
        return icons
    else:
        print("The application " + app_name + " does not exist yet, please report this on GitHub")


def backup(icon, revert=False):
    """
        Backup functions, enables reverting
        @icon: string; the original icon name
        @revert: boolean; True: revert, False: only backup
    """
    back_file = icon + backup_extension
    if path.isfile(icon):
        if not revert:
            copy_file(icon, back_file)
        elif revert:
            move(back_file, icon)


def reinstall():
    """
        Reverts to the original icons
    """
    sni_qt_reverted = False
    apps = get_apps_informations(revert=True)
    if len(apps) != 0:
        for app in apps:
            app_icons = apps[app]["icons"]
            app_path = apps[app]["path"]
            revert_app = apps[app]["name"]
            for icon in app_icons:
                script = False
                if isinstance(icon, list):
                    icon = [item.strip() for item in icon]
                    if len(icon) > 2:
                        script = True
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
                if not script:
                    try:
                        backup(app_path + revert_icon, revert=True)
                    except:
                        continue
                    if revert_app not in reverted_apps:
                        print("%s -- reverted" % (revert_app))
                        reverted_apps.append(revert_app)
                elif script:
                    try:
                        backup(app_path + icon[3], revert=True)
                    except:
                        continue
                    if revert_app not in reverted_apps:
                        print("%s -- reverted" % (revert_app))
                        reverted_apps.append(revert_app)


def install():
    """
        Installs the new supported icons
    """
    apps = get_apps_informations()
    if len(apps) != 0:
        for app in apps:
            app_icons = apps[app]["icons"]
            app_path = apps[app]["path"]
            app_name = apps[app]["name"]
            icon_ctr = 1
            for icon in app_icons:
                script = False
                if isinstance(icon, list):
                    icon = [item.strip() for item in icon]
                    base_icon = path.splitext(icon[0])[0]
                    if len(icon) > 2:
                        script = True
                        script_name = "./" + db_folder + script_folder + icon[2]
                    if theme.lookup_icon(base_icon, default_icon_size, 0):
                        repl_icon = symlink_icon = icon[0]
                    else:
                        symlink_icon = icon[0]  # Hardcoded icon to be replaced
                        repl_icon = icon[1]  # Theme Icon that will replace hardcoded icon
                else:
                    symlink_icon = repl_icon = icon.strip()
                base_icon = path.splitext(repl_icon)[0]
                extension_orig = get_extension(symlink_icon)
                theme_icon = theme.lookup_icon(base_icon, default_icon_size, 0)
                if theme_icon:
                    filename = theme_icon.get_filename()
                    filename_base = path.splitext(path.basename(filename))[0]
                    extension_theme = get_extension(filename)
                    # catching the unrealistic case that theme is neither svg nor png
                    if extension_theme not in ("png", "svg"):
                        exit("Theme icons need to be svg or png files other formats are not supported")
                    if not script:
                        if symlink_icon:
                            output_icon = app_path + symlink_icon
                        else:
                            output_icon = app_path + repl_icon
                        backup(output_icon)
                        if extension_theme == extension_orig:
                            Popen(["ln", "-sf", filename, output_icon])
                            if filename_base not in fixed_icons:
                                print("%s -- fixed using %s" % (app_name, filename_base))
                                fixed_icons.append(filename_base)
                        elif extension_theme == "svg" and extension_orig == "png":
                            try:  # Convert the svg file to a png one
                                with open(filename, "r") as content_file:
                                    svg = content_file.read()
                                fout = open(output_icon, "wb")
                                svg2png(bytestring=bytes(svg, "UTF-8"), write_to=fout)
                                fout.close()
                                chown(output_icon, int(getenv("SUDO_UID")), int(getenv("SUDO_GID")))
                            except:
                                print("The svg file `" + filename + "` is invalid.")
                                continue
                            # to avoid identical messages
                            if not (filename in fixed_icons):
                                print("%s -- fixed using %s" % (app_name, filename_base))
                                fixed_icons.append(filename_base)
                        elif extension_theme == "png" and extension_orig == "svg":
                            print("Theme icon is png and hardcoded icon is svg. There is nothing we can do about that :(")
                            continue
                        else:
                            print("Hardcoded file has to be svg or png. Other formats are not supported yet")
                            continue
                    # Qt applications
                    else:
                        err = None
                        if icon[2] == qt_script:
                            app_sni_qt_prefix = apps[app].get("sniqtprefix", app)
                            app_sni_qt_path = sni_qt_folder + app_sni_qt_prefix + "/"
                            if not path.exists(app_sni_qt_path):
                                makedirs(app_sni_qt_path)
                                chown(app_sni_qt_path, int(getenv("SUDO_UID")), int(getenv("SUDO_GID")))
                            if len(icon) == 4:
                                try:
                                    remove(app_sni_qt_path + symlink_icon)
                                    symlink(app_sni_qt_path + icon[3], app_sni_qt_path + symlink_icon)
                                except FileNotFoundError:
                                    symlink(app_sni_qt_path + icon[3], app_sni_qt_path + symlink_icon)
                            else:
                                if path.isfile(script_name):
                                    p = Popen([script_name, filename, symlink_icon, app_sni_qt_path], stdout=PIPE, stderr=PIPE)
                                    output, err = p.communicate()
                                else:
                                    print("%s -- script file does not exists" % script_name)
                        else:
                            if path.isfile(script_name):
                                backup(app_path + icon[3])
                                if icon_ctr == 1:
                                    do = 0
                                elif icon_ctr == len(app_icons):
                                    do = -1
                                else:
                                    do = 1
                                p = Popen([script_name, filename, symlink_icon, app_path, str(do)], stdout=PIPE, stderr=PIPE)
                                output, err = p.communicate()
                            else:
                                print("%s -- script file does not exists" % script_name)
                        # to avoid identical messages
                        if not (filename in fixed_icons):
                            if not err:
                                print("%s -- fixed using %s" % (app_name, filename_base))
                                fixed_icons.append(filename_base)
                            else:
                                if err not in script_errors:
                                    script_errors.append(err)
                                    err = err.decode("utf-8")
                                    err = "\n".join(["\t" + e for e in err.split("\n")])
                                    print("fixing %s failed with error:\n%s" % (app_name, err))
                icon_ctr += 1
    else:
        exit("No apps to fix! Please report on GitHub if this is not the case")

if detect_de() in ("pantheon", "xfce"):
    default_icon_size = 24

print("Welcome to the tray icons hardcoder fixer!")
print("Your indicator icon size is : %s" % default_icon_size)
print("Your current icon theme is : %s" % theme_name)
print("1 - Install")
print("2 - Reinstall")
try:
    choice = int(input("Please choose: "))
    if choice == 1:
        print("Installing now..\n")
        install()
    elif choice == 2:
        print("Reinstalling now..\n")
        reinstall()
    else:
        exit("Please try again")
except ValueError:
    exit("Please choose a valid value!")

print("\nDone , Thank you for using the Hardcode-Tray fixer!")
