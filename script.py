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
def get_subdirs(d):
    if path.isdir(d):
        dirs = listdir(d)
        dirs.sort()
        result = []
        for a in dirs:
            if path.isdir(d + "/" + a):
                result.append(a)
        return result
    else:
        return None


# Get the icons name from the db directory
def get_icons(app_name):
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


# Gets the dropbox folder
def dropbox_folder(d):
    dirs = d.split("{*}")
    sub_dirs = get_subdirs(dirs[0])
    if sub_dirs:
        sub_dirs.sort()
        if sub_dirs[0].split("-")[0] == "dropbox":
            return dirs[0] + sub_dirs[0] + dirs[1]
        else:
            return None
    else:
        return None


# Converts the csv file to a dictionary
def csv_to_dic():
    db = open(db_file)
    r = reader(db, skipinitialspace=True)
    dic = {}
    for row in r:
        row[1] = row[1].replace("{userhome}", userhome).strip()
        if "{*}" in row[1]:
            row[1] = dropbox_folder(row[1])
        if row[1]:
            if path.isdir(row[1]+"/"):  # check if the folder exists
                icon = get_icons(row[0])
                if icon:
                    if len(row) == 3:
                        dic[row[0]] = {'link': row[1], 'icons': icon, 'sni-qt':row[2]}
                    else:
                        dic[row[0]] = {'link': row[1], 'icons': icon}
                else:
                    continue
        else:
            continue
    db.close()
    return dic

def convert2svg(filename,output_file):
    with open(filename, 'r') as content_file:
        svg = content_file.read()
    fout = open(output_file, 'wb')
    svg2png(bytestring=bytes(svg, 'UTF-8'), write_to=fout)
    fout.close()

# Copy files..
def copy_files():
    apps = csv_to_dic()
    if len(apps) != 0:
        for app in apps:
            app_icons = apps[app]['icons']
            for icon in app_icons:
                script = False
                if isinstance(icon, list):
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
                    symlink_icon = repl_icon = icon
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
                            output = apps[app]['link'] + "/" + symlink_icon
                        else:
                            output = apps[app]['link'] + "/" + repl_icon  # Output icon
                        if extension_theme == extension_orig:
                            Popen(['ln', '-sf', filename, output])
                            print("%s -- fixed using %s" % (app, filename))
                        elif extension_theme == '.svg' and extension_orig == '.png':
                            try:
                                convert2svg(filename,output)
                            except:
                                print("The svg file `" + filename + "` is invalid.")
                                continue
                            chown(output, int(getenv('SUDO_UID')), int(getenv('SUDO_GID')))
                            print("%s -- fixed using %s" % (app, filename))
                        elif extension_theme == '.png' and extension_orig == '.svg':
                            print('Theme icon is png and hardcoded icon is svg. There is nothing we can do about that :(')
                            continue
                        else:
                            print('Hardcoded file has to be svg or png. Other formats are not supported yet')
                            continue
                    else: #Sni-qt icons & Chrome/Spotify script 
                        folder = apps[app]['link']
                        if apps[app]['sni-qt']:
                            sni_qt = apps[app]['sni-qt']
                        else:
                            sni_qt = app
                        new_path = sni_qt_folder + sni_qt
                        if icon[2] == qt_script:
                            if not path.exists(new_path):
                                makedirs(new_path)
                                chown(new_path, int(getenv('SUDO_UID')), int(getenv('SUDO_GID')))
                            if len(icon) == 4:
                                call([script_name, filename, symlink_icon, new_path, icon[3]], stdout=PIPE, stderr=PIPE)
                            else:
                                call([script_name, filename, symlink_icon, new_path], stdout=PIPE, stderr=PIPE)
                        else:
                            call([script_name, filename, symlink_icon, folder], stdout=PIPE, stderr=PIPE)
                        print("%s -- fixed using %s" % (app, filename))
                else:
                    print("%s -- theme icon not found. You should report that to the theme maintainer!" %(base_icon))
    else:
        exit("No apps to fix! Please report on GitHub if this is not the case")

if detect_de() in ('pantheon', 'xfce'):
    default_icon_size = 24

# The message shown to the user
print("Welcome to the tray icons hardcoder fixer! \n")
print("Copying now..\n")
copy_files()
print("\nDone , Thank you for using the Hardcode-Tray fixer!")
