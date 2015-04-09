__author__ = "Bilal ELMOUSSAOUI"
version = 0.1

import os,pwd
global db_file,folder_icons,extra_folder,username

db_file = "db.csv"
extra_folder = "extra"
folder_icons = "/usr/share/icons"
supported_theme = []
username = pwd.getpwuid( os.getuid() )[ 0 ]
os = os.system("lsb_release -si")
default_icon_size = "24x24"
if os == "elementary OS":
	default_icon_size = "22x22"

#Check if the directory exists
def is_dir(dir):
	return os.path.isdir(dir)

#create a link from a list
def do_link(ls,start=False):
	return "/".join(ls)

#get all the supported themes
def check_supported_themes():
	themes = os.listdir(folder_icons)
	themes_supported = []
	for theme in themes:
		if is_dir(do_link([folder_icons,theme])):
			if is_dir(do_link([folder_icons,theme,extra_folder])):
				themes_supported.append(theme)
	return themes_supported

#get all the supported apps in a theme
def check_supported_apps(theme):
	apps_supported = []
	apps = os.listdir(do_link([folder_icons,theme,extra_folder]))
	for app in apps:
		if is_dir(do_link([folder_icons,theme,extra_folder,app])):
			apps_supported.append(app)
	return apps_supported

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
		if infos[i][0] not in dic.keys():
			dic[infos[i][0]] = infos[i]
	return dic

#creat a symlink of all the files.
def deep_copy(src,des):
	files = os.listdir(src)
	for f in files:
		if not is_dir(do_link([src,f])):
			os.system("sudo ln -fns "+do_link([src,f]) + " "+des)
		else:
			deep_copy(do_link([src,f]),do_link([des,f]))

#Copy files..
def copy_files(theme):
	apps_in_theme = check_supported_apps(theme)
	apps_by_hardcoder = csv_to_dic()
	for app in apps_in_theme:
		if app in apps_by_hardcoder.keys() and is_dir("/"+apps_by_hardcoder[app][1]+"/"):
			o_folder = "/"+apps_by_hardcoder[app][1] #Original folder
			i_folder = do_link(["/usr/share/icons/",theme,extra_folder,app,default_icon_size])#Icons folder
			deep_copy(i_folder,o_folder)

supported_theme = check_supported_themes()
l_supported_theme = len(supported_theme)

#The message shown to the user
message = "Welcome to the tray icons hardcoder fixer! Please choose one of the supported themes\n"
if l_supported_theme == 0:
	print(message+ "No theme is supported at the moment.. please update your themes!")
else:
	for i in range(l_supported_theme):
		message+= str(i+1) + " - " +supported_theme[i]
		message += "\n"
	chosen_theme = int(input(message))-1

	if chosen_theme >= l_supported_theme or chosen_theme < 0:
		raise Exception("The chosen theme dosen't exists, please try again")
	else:
		theme = supported_theme[chosen_theme]
		supported_apps = check_supported_apps(theme)
		if len(supported_apps) == 0:
			print("The chosen theme dosen't support any application at the moment")
		else:
			print("You did choice "+theme+", the supported applications by your theme are : "+ ", ".join(supported_apps)+"\n")
			print("Copying now..\n")
			copy_files(theme)
			print("Done , Thank you for using the Hardcode-Tray fixer!")
