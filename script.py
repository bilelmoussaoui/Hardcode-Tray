__author__ = "Bilal ELMOUSSAOUI"
version = 0.1

import os,pwd,platform,csv
from gi.repository import Gtk
global db_file,folder_icons,username,theme,default_icon_size

db_file = "db.csv"
folder_icons = "/usr/share/icons"
username = pwd.getpwuid( os.getuid() )[ 0 ]
useros = platform.linux_distribution()
useros = useros[0].strip('"')
theme = Gtk.IconTheme.get_default()
default_icon_size = 22
if useros == 'elementary OS' or useros == 'XFCE':
	default_icon_size = 24

#Check if the directory exists
def is_dir(dir):
	return os.path.isdir(dir)

#create a link from a list
def do_link(ls,start=False):
	return "/".join(ls)

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
			if theme.lookup_icon(icon, default_icon_size, 0):
				o_folder = "/"+apps[app][1] #Original folder
				i_folder = theme.lookup_icon(icon, default_icon_size, 0).get_filename()#Icons folder
				os.system("sudo ln -fns "+i_folder + " "+o_folder)

#The message shown to the user
print("Welcome to the tray icons hardcoder fixer! \n")
print("Copying now..\n")
copy_files()
print("Done , Thank you for using the Hardcode-Tray fixer!")
