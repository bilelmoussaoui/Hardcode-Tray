__author__ = "Bilal ELMOUSSAOUI"
version = 0.1

import os, pwd, platform, csv, subprocess, sys
import cairosvg
from gi.repository import Gtk

if os.geteuid() != 0:
	sys.exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

db_file = "db.csv"
username = pwd.getpwuid( os.getuid() )[ 0 ]
useros = platform.linux_distribution()
useros = useros[0].strip('"')
theme = Gtk.IconTheme.get_default()

default_icon_size = 22
if useros == 'elementary OS' or detect_desktop_environment()=='xfce':
	default_icon_size = 24

#detect desktop environment
def detect_desktop_environment():
    if os.environ.get('KDE_FULL_SESSION') == 'true':
        return 'kde'
    elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
        return 'gnome'
    else:
        try:
            process = subprocess.Popen(['ls', '-la', 'xprop -root _DT_SAVE_MODE'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out = process.communicate()
            if ' = "xfce4"' in out:
                return 'xfce'
            else:
                return 'generic'
        except (OSError, RuntimeError):
            return 'generic'


#Check if the directory exists
def is_dir(dir):
	return os.path.isdir(dir)

#convert the csv file to a dictionnary 
def csv_to_dic(dark_light):
   	db = open(db_file)
   	r = csv.reader(db)
   	if dark_light == 1:
   		used_theme = "dark"
   	else:
   		used_theme = "light"
   	dic = {}
   	for row in r:
   		row[1] = row[1].replace("{dark_light}",used_theme)
   		if is_dir("/"+row[1]):#check if the folder exists 
   			dic[row[0]] = {'link' :row[1] , 'icons': [row [i] for i in range(2,len(row))]}
   	return dic
#Copy files..
def copy_files(dark_light):
	apps = csv_to_dic(dark_light)
	for app in apps:
		app_icons = apps[app]['icons']
		for icon in app_icons:
			base_icon = os.path.splitext(icon)[0]
			extension_orig = os.path.splitext(icon)[1]
			theme_icon = theme.lookup_icon(base_icon, default_icon_size, 0)
			if theme_icon:
				filename = theme_icon.get_filename()
				extension_theme = os.path.splitext(filename)[1]
				o_file = "/"+apps[app]['link']+"/"+icon #Output icon
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
dark_light = int(input("Do you wish to use light or dark icons? \n 1 - Dark \n 2 - Light \n"))
if not (dark_light in [1,2]):
	sys.exit("Please retry again!")
print("Copying now..\n")
copy_files(dark_light)
print("\nDone , Thank you for using the Hardcode-Tray fixer!")