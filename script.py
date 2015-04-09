__author__ = "Bilal ELMOUSSAOUI"
version = 0.1

import os, pwd, platform, csv, subprocess, sys
import cairosvg
from gi.repository import Gtk
#global db_file,username,theme,default_icon_size

if os.geteuid() != 0:
    sys.exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

db_file = "db.csv"
username = pwd.getpwuid( os.getuid() )[ 0 ]
useros = platform.linux_distribution()
useros = useros[0].strip('"')
theme = Gtk.IconTheme.get_default()
default_icon_size = 22
if useros == 'elementary OS' or useros == 'Xubuntu':
    default_icon_size = 24

#Check if the directory exists
def is_dir(dir):
    return os.path.isdir(dir)

#convert the csv file to a dictionnary 
def csv_to_dic():
    d = open(db_file)
    content = d.readlines()
    d.close()
    dic = {}
    infos = []
    for i in range(len(content)):
        infos.append(content[i].strip("\n").split(","))
        infos[i][1] = infos[i][1].replace("{user_name}",username)
        if infos[i][0] not in dic.keys() and is_dir("/"+infos[i][1]):
            dic[infos[i][0]] = infos[i]
    return dic

def get_icons(app,apps):
    i = 2
    icons = [] 
    while i < len(apps[app]):
        icons.append(apps[app][i])
        i+=1
    return icons

#Copy files..
def copy_files():
    apps = csv_to_dic()
    for app in apps:
        app_icons = get_icons(app,apps)
        for icon in app_icons:
            base_icon = os.path.splitext(icon)[0]
            extension_orig = os.path.splitext(icon)[1]
            theme_icon = theme.lookup_icon(base_icon, default_icon_size, 0)
            if theme_icon:
                filename = theme_icon.get_filename()
                extension_theme = os.path.splitext(filename)[1]
                o_file = "/"+apps[app][1]+"/"+icon #Output icon
                if extension_theme == extension_orig:
                    subprocess.Popen(['ln', '-sf', filename, o_file])
                    print("%s -- fixed using %s"%(app, filename))
                elif extension_theme == '.svg' and extension_orig == '.png':
                    with open(filename, 'r') as content_file:
                        svg = content_file.read()
                    fout = open(o_file,'wb')
                    cairosvg.svg2png(bytestring=bytes(svg,'UTF-8'),write_to=fout)
                    fout.close()
                    print("%s -- fixed using %s"%(app, filename))
                else:
                    sys.exit('hardcoded file has to be svg or png. Other formats not supported yet')
        

#The message shown to the user
print("Welcome to the tray icons hardcoder fixer! \n")
print("Copying now..\n")
copy_files()
print("\nDone , Thank you for using the Hardcode-Tray fixer!")
