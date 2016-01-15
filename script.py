#!/usr/bin/python3
"""
Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 2.3
Website : https://github.com/bil-elmoussaoui/Hardcode-Tray
Licence : The script is released under GPL,
        uses some icons and a modified script form Chromium project
        released under BSD license
"""

from csv import reader
from os import environ, geteuid, getlogin, listdir, path, makedirs, chown,\
    getenv, symlink, remove
from subprocess import Popen, PIPE, check_output, call
from sys import exit, argv
from shutil import rmtree, copyfile, move
from hashlib import md5
from imp import load_source
from collections import OrderedDict

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

try:
    svgtopng = load_source("svgtopng", "./database/scripts/svgtopng.py")
except FileNotFoundError:
    exit("You need to clone the whole repository to use the script.")

if geteuid() != 0:
    exit("You need to have root privileges to run the script.\
        \nPlease try again, this time using 'sudo'. Exiting.")

if not environ.get("DESKTOP_SESSION"):
    exit("You need to run the script using 'sudo -E'.\nPlease try again")

db_file = "db.csv"
backup_extension = ".bak"
userhome = check_output('sh -c "echo $HOME"', universal_newlines=True,
                        shell=True).strip()
gsettings = Gio.Settings.new("org.gnome.desktop.interface")
db_folder = "database/"
script_folder = "scripts/"
absolute_path = path.split(path.abspath(__file__))[0] + "/"
sni_qt_folder = userhome + "/.local/share/sni-qt/icons/"
images_folder = absolute_path + db_folder + "images/"
theme = Gtk.IconTheme.get_default()
theme_name = str(gsettings.get_value("icon-theme")).strip("'")
qt_script = "qt-tray"
default_icon_size = 22
backup_ignore_list = ["hexchat"]
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
        return sub_dirs
    else:
        return None


def mchown(directory):
    """
        Fix folder/file permissions
        Args:
            directory (str): folder/file path
    """
    path_list = directory.split("/")
    dir_path = "/"
    for directory in path_list:
        dir_path += str(directory) + "/"
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


def compare_two_images(file1path, file2path):
    """
        Compare two images/files
        Args:
            file1path : String; The path to the first file
            file2path : String; The path to the second file
        Returns:
            bool
    """
    if path.isfile(file1path) and path.isfile(file2path):
        first_content = open(file1path, "rb").read()
        second_content = open(file2path, "rb").read()
        return md5(first_content).hexdigest() == md5(second_content).hexdigest()


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


def filter_icon(list_icons, value):
    """
        Returns an integer:  the index of an icon in list
        Args:
            list_icons(list): list of icons with sublist
            value(str): The name of icon that you're looking for
    """
    for i in range(len(list_icons)):
        for j in range(len(list_icons[i])):
            if list_icons[i][j] == value:
                return i


def get_correct_chrome_icons(apps_infos, pak_file="chrome_100_percent.pak"):
    """
        Returns the correct chrome indicator icons name in the pak file
        Args:
            apps_infos(list): Contains the information's in the database file
            pak_file(str): The pak file name
    """
    images_dir = images_folder + "chromium/"
    dirname = absolute_path + db_folder + script_folder
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
            for default_icon in default_icons:
                default_icon_path = images_dir + default_icon + ".png"
                if compare_two_images(icon, default_icon_path):
                    list_icons[default_icon] = icon
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
        Args:
            directory(str): the default dropbox directory
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
    return supported_app


def get_apps_informations(fix_only):
    """
        Reads the database file and returns a dictionary with all information
        Args:
            @fix_only (list): contains a list of applications to be fixed/reverted
    """
    db = open(db_file)
    r = reader(db, skipinitialspace=True)
    next(r)
    apps = OrderedDict()
    ctr = 0
    fix_only = fix_only if fix_only else get_supported_apps()
    for app in r:
        if app[1] in fix_only:
            app[2] = app[2].replace("{userhome}", userhome).strip()
            if "{dropbox}" in app[2]:
                app[2] = replace_dropbox_dir(app[2])
            if app[1] == "hexchat":
                create_hexchat_dir(app)
            if app[2]:
                if path.isdir(app[2]) or path.isfile(app[2]):
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
                        apps[app_name]["path"] = app[2]
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


def reinstall(fix_only):
    """
        Reverts to the original icons
    """
    sni_qt_reverted = False
    apps = get_apps_informations(fix_only)
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


def install(fix_only):
    """
        Installs the new supported icons
    """
    apps = get_apps_informations(fix_only)
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
                                apps[app]["icons"][filter_icon(app_icons, new_icon)][0] = real_icons[new_icon]
                else:
                    dont_install = True
            icon_ctr = 1
            while icon_ctr <= len(app_icons) and not dont_install:
                icon = app_icons[icon_ctr - 1]
                is_script = False
                if isinstance(icon, list):
                    icon = [item.strip() for item in icon]
                    base_icon = path.splitext(icon[0])[0]
                    symlink_icon = path.splitext(icon[1])[0]
                    if len(icon) > 2:
                        is_script = True
                        sfile = "./" + db_folder + script_folder + icon[2]
                    if theme.lookup_icon(symlink_icon, default_icon_size, 0):
                        repl_icon = icon[1]
                        symlink_icon = icon[0]
                    else:
                        repl_icon = symlink_icon = icon[0]
                else:
                    symlink_icon = repl_icon = icon.strip()
                base_icon = path.splitext(repl_icon)[0]
                ext_orig = get_extension(symlink_icon)
                theme_icon = theme.lookup_icon(base_icon, default_icon_size, 0)
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
                                print("%s -- fixed using %s" % (app_name, fbase))
                                fixed_icons.append(fbase)
                        elif ext_theme == "svg" and ext_orig == "png":
                            if svgtopng.is_svg_enabled():
                                try:  # Convert the svg file to a png one
                                    svgtopng.convert_svg2png(fname, output_icon)
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
                                    execute([sfile, fname, symlink_icon,
                                            app_path, str(do), icon[3]])
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

fix_only = False
if len(argv) > 1 and argv[1] == "--only":
    if len(argv) > 2:
        fix_only = argv[2].lower().strip().split(",")
    else:
        fix_only = False
        
print("Welcome to the tray icons hardcoder fixer!")
print("Your indicator icon size is : %s" % default_icon_size)
print("Your current icon theme is : %s" % theme_name)
print("Svg to png functions are : ", end ="")
print("Enabled" if svgtopng.is_svg_enabled() else "Disabled")
print("Applications will be fixed : ", end ="")
print(",".join(fix_only) if fix_only else "All")
print("1 - Apply")
print("2 - Revert")
try:
    choice = int(input("Please choose: "))
    if choice == 1:
        print("Applying now..\n")
        install(fix_only)
    elif choice == 2:
        print("Reverting now..\n")
        reinstall(fix_only)
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
