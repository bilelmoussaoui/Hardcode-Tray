#!/usr/bin/python3

from csv import reader
from gi.repository import Gtk
from os import environ, geteuid, getlogin, listdir, path, makedirs, chown, getenv
from subprocess import Popen, PIPE, call
from platform import linux_distribution
from sys import exit

try:
    from cairosvg import svg2png
except:
    exit("You need to install python3-cairosvg to run this script.\nPlease install it and try again. Exiting.")

if geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

db_file = "db.csv"
db_folder = "database"
script_folder = "scripts"
userhome = path.expanduser('~' + getlogin())
sni_qt_folder = userhome + "/.local/share/sni-qt/icons/"
theme = Gtk.IconTheme.get_default()
qt_script = "qt-tray"
default_icon_size = 22
fixed_icons = []
script_errors = []

# Detects the desktop environment
def detect_de():
    if environ.get('DESKTOP_SESSION') == 'pantheon' or linux_distribution()[0].strip('"') == "elementary OS":
        return 'pantheon'
    else:
        try:
            process = Popen(['ls', '-la', 'xprop -root _DT_SAVE_MODE'], stdout=PIPE, stderr=PIPE)
            out = process.communicate()
            if ' = "xfce4"' in out:
                return 'xfce'
            else:
                return 'other'
        except (OSError, RuntimeError):
            return 'other'


# Creates a list of subdirectories
def get_subdirs(directory):
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


# Get the icons name from the db directory
def get_app_icons(app_name):
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


# Correct/get the original dropbox directory
def replace_dropbox_dir(d):
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


# Converts the csv database to a dictionary
def csv_to_dic():
    db = open(db_file)
    r = reader(db, skipinitialspace=True)
    apps = {}
    for app in r:
        app[1] = app[1].replace("{userhome}", userhome).strip()
        if "{dropbox}" in app[1]:
            app[1] = replace_dropbox_dir(app[1])
        if app[1]:
            if path.isdir(app[1]+"/"):  # check if the folder exists
                icons = get_app_icons(app[0])
                if icons:
                    if len(app) == 3:
                        apps[app[0]] = {'link': app[1], 'icons': icons, 'sni-qt':app[2]}
                    else:
                        apps[app[0]] = {'link': app[1], 'icons': icons}
                else:
                    continue
        else:
            continue
    db.close()
    return apps

# Copy files..
def copy_files():
    apps = csv_to_dic()
    if len(apps) != 0:
        for app in apps:
            app_icons = apps[app]['icons']
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
                    if extension_theme not in ('.png', '.svg'): #catching the unrealistic case that theme is neither svg nor png
                        exit('Theme icons need to be svg or png files other formats are not supported')
                    if not script:
                        if symlink_icon:
                            output_icon = apps[app]['link'] + "/" + symlink_icon
                        else:
                            output_icon = apps[app]['link'] + "/" + repl_icon  # Output icon
                        if extension_theme == extension_orig:
                            Popen(['ln', '-sf', filename, output_icon])
                            print("%s -- fixed using %s" % (app, filename))
                        elif extension_theme == '.svg' and extension_orig == '.png':
                            try:#Convert the svg file to a png one
                                with open(filename, 'r') as content_file:
                                    svg = content_file.read()
                                fout = open(output_icon, 'wb')
                                svg2png(bytestring=bytes(svg, 'UTF-8'), write_to=fout)
                                fout.close()
                                chown(output_icon, int(getenv('SUDO_UID')), int(getenv('SUDO_GID')))
                            except:
                                print("The svg file `" + filename + "` is invalid.")
                                continue
                            #to avoid identical messages
                            if not (filename in fixed_icons):
                                print("%s -- fixed using %s" % (app, filename))
                                fixed_icons.append(filename)
                        elif extension_theme == '.png' and extension_orig == '.svg':
                            print('Theme icon is png and hardcoded icon is svg. There is nothing we can do about that :(')
                            continue
                        else:
                            print('Hardcoded file has to be svg or png. Other formats are not supported yet')
                            continue
                    else: #Sni-qt icons & Chrome/Spotify script 
                        folder = apps[app]['link']
                        app_sni_qt_prefix = apps[app].get("sni-qt", app)
                        app_sni_qt_path = sni_qt_folder + app_sni_qt_prefix
                        #Check if it's a Qt indicator icon
                        if icon[2] == qt_script:
                            #Create a new folder and give permissions to normal user
                            if not path.exists(app_sni_qt_path): 
                                makedirs(app_sni_qt_path)
                                chown(app_sni_qt_path, int(getenv('SUDO_UID')), int(getenv('SUDO_GID')))
                            #If the sni-qt icon can be symlinked to an other one
                            if len(icon) == 4:
                                p = Popen([script_name, filename, symlink_icon, app_sni_qt_path, icon[3]], stdout=PIPE, stderr=PIPE)
                                output, err = p.communicate()
                            else:
                                p = Popen([script_name, filename, symlink_icon, app_sni_qt_path], stdout=PIPE, stderr=PIPE)
                                output, err = p.communicate()
                        else:
                            p = Popen([script_name, filename, symlink_icon, folder], stdout=PIPE, stderr=PIPE)
                            output, err = p.communicate()
                        #to avoid identical messages
                        if not (filename in fixed_icons):
                            if not err:
                                print("%s -- fixed using %s" % (app, filename))
                                fixed_icons.append(filename)
                            else: 
                                if not err in script_errors:
                                    print("fixing %s failed with error:\n"%(app))
                                    print(err.decode('ascii')+'\n')
                                    script_errors.append(err)
    else:
        exit("No apps to fix! Please report on GitHub if this is not the case")

if detect_de() in ('pantheon', 'xfce'):
    default_icon_size = 24

# The message shown to the user
print("Welcome to the tray icons hardcoder fixer! \n")
print("Copying now..\n")
copy_files()
print("\nDone , Thank you for using the Hardcode-Tray fixer!")
