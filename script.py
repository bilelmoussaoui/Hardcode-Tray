#!/usr/bin/python3
'''
Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer , Joshua Fogg
Version : 2.0
Licence : The script is released under GPL,
        uses some icons and a modified script form Chromium project
        released under BSD license
'''

from csv import reader
from gi.repository import Gtk, Gio
from os import environ, geteuid, getlogin, listdir, path, makedirs, chown,\
    getenv, symlink, remove
from subprocess import Popen, PIPE
from sys import exit
from shutil import rmtree, copyfile, move
from hashlib import md5
from collections import OrderedDict
try:
    from cairosvg import svg2png
except ImportError:
    exit("You need to install python3-cairosvg to run this script.\
        \nPlease install it and try again. Exiting.")

if geteuid() != 0:
    exit("You need to have root privileges to run this script.\
        \nPlease try again, this time using 'sudo'. Exiting.")

if not environ.get("DESKTOP_SESSION"):
    exit("You need to run the script using 'sudo -E'.\nPlease try again")

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
    if "pantheon" == environ.get("DESKTOP_SESSION").lower():
        return "pantheon"
    else:
        try:
            out = execute(["ls", "-la", "xprop -root _DT_SAVE_MODE"])
            if " = \"xfce4\"" in out.decode('utf-8'):
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


def mchown(path):
    chown(path, int(getenv("SUDO_UID")), int(getenv("SUDO_GID")))


def create_dir(folder):
    if not path.isdir(folder):
        makedirs(folder, exist_ok=True)
    mchown(folder)


def execute(command_list):
    """
        Run a command using Popen
        @command_list: List;
    """
    p = Popen(command_list, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
    if err and err not in script_errors:
        script_errors.append(err)
    return output


def compare_two_images(file1path, file2path):
    """
        Compare two images/files
        @file1path : String; The path to the first file
        @file2path : String; The path to the second file
    """
    if path.isfile(file1path) and path.isfile(file2path):
        fcontent = open(file1path, "rb").read()
        scontent = open(file2path, "rb").read()
        return md5(fcontent).hexdigest() == md5(scontent).hexdigest()


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


def get_correct_chrome_icons(apps_infos, pak_file="chrome_100_percent.pak"):
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
    if path.isfile(apps_infos["path"] + pak_file):
        copy_file(apps_infos["path"] + pak_file, dirname + pak_file, True)
        create_dir(path.dirname(extracted))
        execute([dirname + "data_pack.py", dirname + pak_file])
        for file_name in listdir(extracted):
            icon = extracted + file_name
            if path.isfile(icon):
                for default_icon in default_icons:
                    default_icon_path = images_dir + default_icon + ".png"
                    if compare_two_images(icon, default_icon_path):
                        list_icons[default_icon] = icon
            else:
                break
        if not list_icons or len(list_icons) < len(default_icons):
            if path.isdir(extracted):
                rmtree(extracted)
            if path.isfile(dirname + pak_file):
                remove(dirname + pak_file)
            return None
        else:
            return list_icons
    else:
        return None


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
        app[2] = app[2].replace("{userhome}", userhome).strip()
        if "{dropbox}" in app[2]:
            app[2] = replace_dropbox_dir(app[2])
        if app[1] == "hexchat":
            app_path = app[2].strip("/").split("/")
            icons_dir = app_path[len(app_path) - 1]
            del app_path[len(app_path) - 1]
            app_path = "/".join(app_path) + "/"
            if path.isdir(app_path):
                create_dir(app_path + icons_dir + "/")
        if app[2]:
            if path.isdir(app[2]) or path.isfile(app[2]):
                icons = get_app_icons(app[1])
                if icons:
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
            app_dbfile = apps[app]["dbfile"]
            app_name = apps[app]["name"]
            dont_install = False
            if app_dbfile in ("google-chrome", "chromium"):
                pak_file = app_icons[0][3]
                real_icons = get_correct_chrome_icons(apps[app], pak_file)
                if real_icons:
                    for new_icon in real_icons:
                        for old_icon in app_icons:
                            if old_icon[1] == new_icon:
                                apps[app]["icons"][filter_icon(apps_icons, new_icon)][0] = real_icons[new_icon]
                else:
                    dont_install = True
            icon_ctr = 1
            while icon_ctr <= len(app_icons) and not dont_install:
                icon = app_icons[icon_ctr - 1]
                script = False
                if isinstance(icon, list):
                    icon = [item.strip() for item in icon]
                    base_icon = path.splitext(icon[0])[0]
                    if len(icon) > 2:
                        script = True
                        sfile = "./" + db_folder + script_folder + icon[2]
                    if theme.lookup_icon(base_icon, default_icon_size, 0):
                        repl_icon = symlink_icon = icon[0]
                    else:
                        # Hardcoded icon to be replaced
                        symlink_icon = icon[0]
                        # Theme Icon that will replace hardcoded icon
                        repl_icon = icon[1]
                else:
                    symlink_icon = repl_icon = icon.strip()
                base_icon = path.splitext(repl_icon)[0]
                ext_orig = get_extension(symlink_icon)
                theme_icon = theme.lookup_icon(base_icon, default_icon_size, 0)
                if theme_icon:
                    fname = theme_icon.get_filename()
                    fbase = path.splitext(path.basename(fname))[0]
                    ext_theme = get_extension(fname)
                    # catching the unrealistic case that theme is neither svg nor png
                    if ext_theme not in ("png", "svg"):
                        exit("Theme icons need to be svg or png files.\
                            \nOther formats are not supported yet")
                    if not script:
                        if symlink_icon:
                            output_icon = app_path + symlink_icon
                        else:
                            output_icon = app_path + repl_icon
                        backup(output_icon)
                        if ext_theme == ext_orig:
                            execute(["ln", "-sf", fname, output_icon])
                            if fbase not in fixed_icons:
                                print("%s -- fixed using %s" % (app_name, fbase))
                                fixed_icons.append(fbase)
                        elif ext_theme == "svg" and ext_orig == "png":
                            try:  # Convert the svg file to a png one
                                with open(fname, "r") as content_file:
                                    svg = content_file.read()
                                fout = open(output_icon, "wb")
                                svg2png(bytestring=bytes(svg, "UTF-8"), write_to=fout)
                                fout.close()
                                mchown(output_icon)
                            except:
                                print("The svg file `%s` is invalid." % fname)
                                continue
                            # to avoid identical messages
                            if not (fbase in fixed_icons):
                                print("%s -- fixed using %s" % (app_name, fbase))
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
                        if icon[2] == qt_script:
                            sni_qt_path = sni_qt_folder + apps[app].get("sniqtprefix", app) + "/"
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
                                    execute([sfile, fname, symlink_icon, sni_qt_path])
                                else:
                                    print("%s -- script file does not exists" % sfile)
                        else:
                            if path.isfile(sfile):
                                backup(app_path + icon[3])
                                if icon_ctr == 1:
                                    do = 0
                                elif icon_ctr == len(app_icons):
                                    do = -1
                                else:
                                    do = 1
                                execute([sfile, fname, symlink_icon, app_path, str(do)])
                            else:
                                print("%s -- script file does not exists" % sfile)
                        # to avoid identical messages
                        if not (fbase in fixed_icons):
                            print("%s -- fixed using %s" % (app_name, fbase))
                            fixed_icons.append(fbase)
                icon_ctr += 1

    else:
        exit("No apps to fix! Please report on GitHub if this is not the case")

if detect_de() in ("pantheon", "xfce"):
    default_icon_size = 24

print("Welcome to the tray icons hardcoder fixer!")
print("Your indicator icon size is : %s" % default_icon_size)
print("Your current icon theme is : %s" % theme_name)
print("1 - Apply")
print("2 - Revert")
try:
    choice = int(input("Please choose: "))
    if choice == 1:
        print("Applying now..\n")
        install()
    elif choice == 2:
        print("Reverting now..\n")
        reinstall()
    else:
        exit("Please try again")
except ValueError:
    exit("Please choose a valid value!")

if len(script_errors) != 0:
    for err in script_errors:
        err = err.decode("utf-8")
        err = "\n".join(["\t" + e for e in err.split("\n")])
        print("fixing failed with error:\n%s" % err)
print("\nDone , Thank you for using the Hardcode-Tray fixer!")
