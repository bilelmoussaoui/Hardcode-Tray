#!/usr/bin/python3
'''
Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : wa4557 , Foggalong
Credits : Hwang, C. W. (hikipro95@gmail.com)
Version : 1.0
Licence : GPL
'''

from csv import reader
from gi.repository import Gtk
from os import environ, geteuid, getlogin, listdir, path, makedirs, chown, getenv, symlink, remove
from subprocess import Popen, PIPE, call
from sys import exit
from shutil import rmtree, copyfile, move
try:
    from cairosvg import svg2png
except ImportError:
    exit("You need to install python3-cairosvg to run this script.\nPlease install it and try again. Exiting.")

if geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

if not environ.get("DESKTOP_SESSION"):
    exit("Please run the script using 'sudo -E' to preserve environment variables")

db_file = "db.csv"
db_folder = "database"
script_folder = "scripts"
userhome = path.expanduser("~" + getlogin())
sni_qt_folder = userhome + "/.local/share/sni-qt/icons/"
theme = Gtk.IconTheme.get_default()
qt_script = "qt-tray"
default_icon_size = 22
fixed_icons = []
reverted_icons = []
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


# Creates a list of subdirectories
def get_subdirs(directory):
    """
        Return a list of subdirectories, used in replace_dropbox_dir
        @directory : String, the path of the directory 
    """
    if path.isdir(directory):
        dirs = listdir(directory)
        dirs.sort()
        sub_dirs = []
        for d in sub_dirs:
            if path.isdir(directory + "/" + a):
                sub_dirs.append(a)
        return sub_dirs
    else:
        return None


def copy_file(src, dest, overwrite=False):
    """
        Simple copy file function with the possibility to overwrite the file
        @src : String, the source file
        @dest : String, the destination folder 
        @overwrite : Boolean, to overwrite the file 
    """
    if overwrite:
        copyfile(src, dest)
    else:
        if not path.isfile(dest):
            copyfile(src, dest)


def get_app_icons(app_name):
    """
        get a list of icons in /database/applicationname of each application 
        @app_name : String, the application name
    """
    if path.isfile(db_folder + "/" + app_name):
        f = open(db_folder + "/" + app_name)
        r = reader(f, skipinitialspace=True)
        icons = []
        for icon in r:
            if icon != "":
                if len(icon) != 1:
                    icons.append(icon)
                else:
                    icons.extend(icon)
        f.close()
        return icons
    else:
        print("The application " + app_name + " does not exist yet, please report this on GitHub")
        return None


def replace_dropbox_dir(d):
    """
        Correct the hardcoded dropbox directory
        @d : String, the default dropbox directory
    """
    dirs = d.split("{dropbox}")
    sub_dirs = get_subdirs(dirs[0])
    if sub_dirs:
        sub_dirs.sort()
        if sub_dirs[0].split("-")[0] == "dropbox":
            return dirs[0] + sub_dirs[0] + dirs[1]
        else:
            return None
    else:
        return None


def csv_to_dic():
    """
        Read the database file and return a dictionnary with all the informations needed
    """
    db = open(db_file)
    r = reader(db, skipinitialspace=True)
    apps = {}
    for app in r:
        app[1] = app[1].replace("{userhome}", userhome).strip()
        if "{dropbox}" in app[1]:
            app[1] = replace_dropbox_dir(app[1])
        if app[1]:
            if path.isdir(app[1] + "/"):
                icons = get_app_icons(app[0])
                if icons:
                    if len(app) == 3:
                        apps[app[0]] = {"link": app[1], "icons": icons, "sni-qt":app[2]}
                    else:
                        apps[app[0]] = {"link": app[1], "icons": icons}
                else:
                    continue
        else:
            continue
    db.close()
    return apps


def backup(icon, revert=False):
    """
        A backup fonction, used to make reverting to the original icons possible
        @icon : String, the original icon name 
        @revert : Boolean, possibility to revert the icons later 
    """
    back_file = icon + ".bak"
    if not revert:
        copy_file(icon, back_file)
    elif revert:
        move(back_file, icon)


def reinstall():
    """
        Reverting to the original icons
    """
    sni_qt_reverted = False
    apps = csv_to_dic()
    if len(apps) != 0:
        for app in apps:
            app_icons = apps[app]["icons"]
            folder = apps[app]["link"]
            for icon in app_icons:
                script = False
                if isinstance(icon, list):
                    icon = [item.strip() for item in icon] 
                    if len(icon) > 2:
                        script = True
                        if icon[2] == qt_script:
                            if sni_qt_reverted: continue
                            if path.exists(sni_qt_folder):
                                rmtree(sni_qt_folder)
                                print("hardcoded Qt apps reverted")
                            sni_qt_reverted = True
                            continue
                    else:
                        revert_icon = icon[0]  #Hardcoded icon to be reverted
                else:
                    revert_icon = icon.strip()
                if not script:
                    try:
                        backup(folder + "/" + revert_icon, revert=True)
                    except:
                        continue
                    if not revert_icon in reverted_icons:
                        print("%s -- reverted" % (revert_icon))
                        reverted_icons.append(revert_icon)
                elif script:
                    try:
                        backup(folder + "/" + icon[3], revert=True)
                    except:
                        continue
                    if not icon[2] in reverted_icons:
                        print("%s -- reverted" % (app))
                        reverted_icons.append(icon[2])
                    
        
def install():
    """
        Installing the new supported icons 
    """
    apps = csv_to_dic()
    if len(apps) != 0:
        for app in apps:
            app_icons = apps[app]["icons"]
            for icon in app_icons:
                script = False
                if isinstance(icon, list):
                    icon = [item.strip() for item in icon] 
                    base_icon = path.splitext(icon[0])[0]
                    if len(icon) > 2:
                        script = True
                        script_name = "./" + db_folder + "/" + script_folder + "/" + icon[2]
                    if theme.lookup_icon(base_icon, default_icon_size, 0):
                        repl_icon = symlink_icon = icon[0]
                    else:
                        symlink_icon = icon[0]  #Hardcoded icon to be replaced
                        repl_icon = icon[1]  #Theme Icon that will replace hardcoded icon
                else:
                    symlink_icon = repl_icon = icon.strip()
                base_icon = path.splitext(repl_icon)[0]
                extension_orig = path.splitext(symlink_icon)[1]
                theme_icon = theme.lookup_icon(base_icon, default_icon_size, 0)
                if theme_icon:
                    filename = theme_icon.get_filename()
                    extension_theme = path.splitext(filename)[1]
                     #catching the unrealistic case that theme is neither svg nor png
                    if extension_theme not in (".png", ".svg"):
                        exit("Theme icons need to be svg or png files other formats are not supported")
                    if not script:
                        if symlink_icon:
                            output_icon = apps[app]["link"] + "/" + symlink_icon
                        else:
                            output_icon = apps[app]["link"] + "/" + repl_icon
                        backup(output_icon)
                        if extension_theme == extension_orig:
                            Popen(["ln", "-sf", filename, output_icon])
                            print("%s -- fixed using %s" % (app, filename))
                        elif extension_theme == ".svg" and extension_orig == ".png":
                            try:#Convert the svg file to a png one
                                with open(filename, "r") as content_file:
                                    svg = content_file.read()
                                fout = open(output_icon, "wb")
                                svg2png(bytestring=bytes(svg, "UTF-8"), write_to=fout)
                                fout.close()
                                chown(output_icon, int(getenv("SUDO_UID")), int(getenv("SUDO_GID")))
                            except:
                                print("The svg file `" + filename + "` is invalid.")
                                continue
                            #to avoid identical messages
                            if not (filename in fixed_icons):
                                print("%s -- fixed using %s" % (app, filename))
                                fixed_icons.append(filename)
                        elif extension_theme == ".png" and extension_orig == ".svg":
                            print("Theme icon is png and hardcoded icon is svg. There is nothing we can do about that :(")
                            continue
                        else:
                            print("Hardcoded file has to be svg or png. Other formats are not supported yet")
                            continue
                    else: #sni-qt icons & Chrome/Spotify script 
                        folder = apps[app]["link"]
                        #Check if it's a Qt indicator icon
                        if icon[2] == qt_script:
                            app_sni_qt_prefix = apps[app].get("sni-qt", app)
                            app_sni_qt_path = sni_qt_folder + app_sni_qt_prefix
                            #Create a new folder and give permissions to normal user
                            if not path.exists(app_sni_qt_path): 
                                makedirs(app_sni_qt_path)
                                chown(app_sni_qt_path, int(getenv("SUDO_UID")), int(getenv("SUDO_GID")))
                            #If the sni-qt icon can be symlinked to an other one
                            if len(icon) == 4:
                                try:
                                    remove(app_sni_qt_path + "/" + symlink_icon)
                                    symlink(app_sni_qt_path + "/" + icon[3], app_sni_qt_path + "/" + symlink_icon)
                                except FileNotFoundError:
                                    symlink(app_sni_qt_path + "/" + icon[3], app_sni_qt_path + "/" + symlink_icon)
                            else:
                                p = Popen([script_name, filename, symlink_icon, app_sni_qt_path], stdout=PIPE, stderr=PIPE)
                                output, err = p.communicate()
                        else:
                            backup(folder + "/" + icon[3])
                            p = Popen([script_name, filename, symlink_icon, folder], stdout=PIPE, stderr=PIPE)
                            output, err = p.communicate()
                        #to avoid identical messages
                        if not (filename in fixed_icons):
                            if not err:
                                print("%s -- fixed using %s" % (app, filename))
                                fixed_icons.append(filename)
                            else: 
                                if not err in script_errors:
                                    script_errors.append(err)
                                    err = err.decode("utf-8")
                                    err = "\n".join(["\t" + e for e in err.split("\n")])
                                    print("fixing %s failed with error:\n%s"%(app, err))
    else:
        exit("No apps to fix! Please report on GitHub if this is not the case")

if detect_de() in ("pantheon", "xfce"):
    default_icon_size = 24

print("Welcome to the tray icons hardcoder fixer! \n")
print("1 - Install \n")
print("2 - Reinstall \n")
try:
    choice  = int(input("Please choose: "))
    if choice == 1:
        print("Installing now..\n")
        install() 
    elif choice == 2:
        print("Reinstalling now..\n")
        reinstall()
    else:   
        exit("Please try again")
except ValueError:
    exit("Please choose a valid value")

print("\nDone , Thank you for using the Hardcode-Tray fixer!")
