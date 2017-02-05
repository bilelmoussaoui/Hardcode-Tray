#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.6.5
Website : https://github.com/bil-elmoussaoui/Hardcode-Tray
Licence : The script is released under GPL, uses a modified script
     form Chromium project released under BSD license
This file is part of Hardcode-Tray.
Hardcode-Tray is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Hardcode-Tray is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Hardcode-Tray. If not, see <http://www.gnu.org/licenses/>.
"""
from os import path, environ, geteuid
from glob import glob
from argparse import ArgumentParser
from modules.parser import Parser
from modules.utils import (execute, change_colors_list, get_scaling_factor,
                           get_list_of_themes, create_icon_theme, detect_de,
                           progress)
from modules.const import DB_FOLDER
from modules.svg.inkscape import Inkscape
from modules.svg.cairosvg import CairoSVG
from modules.svg.rsvgconvert import RSVGConvert
from modules.svg.imagemagick import ImageMagick
from modules.svg.svgexport import SVGExport
from modules.svg.svg import SVG, SVGNotInstalled
import logging


from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk
colours = []
gsettings = None
parser = ArgumentParser(prog="Hardcode-Tray")
absolute_path = path.split(path.abspath(__file__))[0] + "/"
THEMES_LIST = get_list_of_themes()
theme = Gtk.IconTheme.get_default()
SCALING_FACTOR = get_scaling_factor()

CONVERSION_TOOLS = {"Inkscape" : Inkscape, 
                    "CairoSVG" : CairoSVG,
                    "RSVGConvert" : RSVGConvert, 
                    "ImageMagick" : ImageMagick, 
                    "SVGExport" : SVGExport
                    }


parser.add_argument("--debug", "-d", action='store_true',
                    help="Run the script with debug mode.")
parser.add_argument("--size", "-s", help="use a different icon size instead "
                    "of the default one.",
                    type=int, choices=[16, 22, 24])
parser.add_argument("--theme",
                    help="use a different icon theme instead "
                    "of the default one.",
                    type=str, choices=THEMES_LIST)
parser.add_argument("--light-theme", "-lt",
                    help="use a specified theme for the light icons."
                    " Can't be used with --theme."
                    "Works only with --dark-theme.",
                    type=str)
parser.add_argument("--dark-theme", "-dt",
                    help="use a specified theme for the dark icons."
                    "Can't be used with --theme"
                    "Works only with --light-theme.",
                    type=str)
parser.add_argument("--only", "-o",
                    help="fix only one application or more, linked by a ','.\n"
                    "example : --only dropbox,telegram",
                    type=str)
parser.add_argument("--path", "-p",
                    help="use a different icon path for a single icon.",
                    type=str)
parser.add_argument("--update", "-u", action='store_true',
                    help="update Hardcode-Tray to the latest stable version.")
parser.add_argument("--update-git", "-ug", action='store_true',
                    help="update Hardcode-Tray to the latest git commit.")
parser.add_argument("--version", "-v", action='store_true',
                    help="print the version number of Hardcode-Tray.")
parser.add_argument("--apply", "-a", action='store_true',
                    help="fix hardcoded tray icons")
parser.add_argument("--revert", "-r", action='store_true',
                    help="revert fixed hardcoded tray icons")
parser.add_argument("--conversion-tool", "-ct",
                    help="Which of conversion tool to use",
                    type=str, choices=CONVERSION_TOOLS.keys())
parser.add_argument('--change-color', "-cc", type=str, nargs='+',
                    help="Replace a color with an other one, "
                    "works only with SVG.")
args = parser.parse_args()


def get_supported_apps(fix_only, custom_path=""):
    """Get a list of dict, a dict for each supported application."""
    if len(fix_only) != 0:
        database_files = []
        for db_file in fix_only:
            db_file = "{0}{1}.json".format(DB_FOLDER, db_file)
            if path.exists(db_file):
                database_files.append(db_file)
    else:
        database_files = glob("{0}*.json".format(path.join(DB_FOLDER, "")))
    if len(fix_only) > 1 and custom_path:
        exit("You can't use --path with more than application at once.")
    database_files.sort()
    supported_apps = []
    for db_file in database_files:
        application_data = Parser(db_file, theme, svgtopng, default_icon_size, custom_path)
        if application_data.is_installed():
            supported_apps.append(application_data.get_application())
    return supported_apps



def apply(fix_only, custom_path, is_install):
    apps = get_supported_apps(fix_only, custom_path)
    done = []
    if len(apps) != 0:
        cnt = 0
        counter_total = sum(app.data.supported_icons_cnt for app in apps)
        for i, app in enumerate(apps):
            app_name = app.get_name()
            if is_install:
                app.install()
            else:
                app.reinstall()
            if app.is_done:
                cnt += app.data.supported_icons_cnt
                if app_name not in done:
                    progress(cnt, counter_total, app_name)
                    done.append(app_name)
            else:
                counter_total -= app.data.supported_icons_cnt
                if i == len(apps) - 1:
                    progress(cnt, counter_total)
    else:
        if is_install:
            exit("No apps to fix! Please report on GitHub if this is not the case")
        else:
            exit("No apps to revert!")


if geteuid() != 0:
    exit("You need to have root privileges to run the script.\
        \nPlease try again, this time using 'sudo'. Exiting.")

if not (environ.get("DESKTOP_SESSION") or
        environ.get("XDG_CURRENT_DESKTOP")) and not args.size:
    exit("You need to run the script using 'sudo -E'.\nPlease try again")

if args.theme:
    theme_name = args.theme
    theme = create_icon_theme(theme_name, THEMES_LIST)
elif args.light_theme and args.dark_theme:
    light_theme_name = args.light_theme
    dark_theme_name = args.dark_theme
    dark_theme = create_icon_theme(dark_theme_name, THEMES_LIST)
    light_theme = create_icon_theme(light_theme_name, THEMES_LIST)
    theme = {
        "dark": dark_theme,
        "light": light_theme
    }
else:
    source = Gio.SettingsSchemaSource.get_default()
    if source.lookup("org.gnome.desktop.interface", True):
        gsettings = Gio.Settings.new("org.gnome.desktop.interface")
        theme_name = gsettings.get_string("icon-theme")

if args.change_color:
    colours = change_colors_list(args.change_color)

level = logging.ERROR
if args.debug:
    level = logging.DEBUG
logging.basicConfig(level=level,
                    format='[%(levelname)s] - %(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

if args.conversion_tool:
    try:
        svgtopng = CONVERSION_TOOLS[args.conversion_tool](colours)
    except SVGNotInstalled:
        exit("The selected conversion tool is not installed.")
else:
    svgtool_found = False
    for conversion_tool in CONVERSION_TOOLS:
        try:
            svgtopng = CONVERSION_TOOLS[conversion_tool](colours)
            svgtool_found = True
            break
        except SVGNotInstalled:
            svgtool_found = False
            pass
    if not svgtool_found:
        exit("None of the supported conversion tools are installed")


if args.size:
    default_icon_size = args.size
else:
    if detect_de() in ("pantheon", "xfce"):
        default_icon_size = 24
    else:
        default_icon_size = 22
if SCALING_FACTOR != 0:
    default_icon_size *= SCALING_FACTOR
    default_icon_size = round(default_icon_size, 0)
choice = None
fix_only = args.only.lower().strip().split(",") if args.only else []

if args.path and fix_only and len(fix_only) == 1:
    icon_path = args.path
else:
    icon_path = None
if args.apply:
    choice = 1
if args.revert:
    choice = 2
print("Welcome to the tray icons hardcoder fixer!")
print("Your indicator icon size is : %s" % default_icon_size)
if args.theme or gsettings:
    print("Your current icon theme is : %s" % theme_name)
elif args.dark_theme and args.light_theme:
    print("Your current dark icon theme is : %s" % dark_theme_name)
    print("Your current light icon theme is : %s" % light_theme_name)
print("Conversion tool : {0}".format(svgtopng))
print("Applications will be fixed : ", end="")
print(",".join(fix_only) if fix_only else "All")

if not choice:
    print("1 - Apply")
    print("2 - Revert")
    has_chosen = False
    while not has_chosen:
        try:
            choice = int(input("Please choose: "))
            if choice not in [1, 2]:
                print("Please try again")
            else:
                has_chosen = True
        except ValueError:
            print("Please choose a valid value!")
        except KeyboardInterrupt:
            exit("")

if choice == 1:
    print("Applying now..\n")
    apply(fix_only, icon_path, True)
elif choice == 2:
    print("Reverting now..\n")
    apply(fix_only, icon_path, False)

print("\nDone, Thank you for using the Hardcode-Tray fixer!")
