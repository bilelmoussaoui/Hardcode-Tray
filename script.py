#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.6.6
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
from os import path, geteuid
from glob import glob
from argparse import ArgumentParser
from modules.parser import Parser, ArgsParser, CONVERSION_TOOLS
from modules.utils import parse_json, progress, get_list_of_themes
from modules.const import DB_FOLDER, DESKTOP_ENV, CONFIG_FILE


if geteuid() != 0:
    exit("You need to have root privileges to run the script.\
        \nPlease try again, this time using 'sudo'. Exiting.")

parser = ArgumentParser(prog="hardcode-tray")
THEMES_LIST = get_list_of_themes()
config = parse_json(CONFIG_FILE)
BLACKLIST = config.get("blacklist", [])

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
args = ArgsParser(args, config)

if (not DESKTOP_ENV or DESKTOP_ENV == "other") and not args.icon_size:
    exit("You need to run the script using 'sudo -E'.\nPlease try again")

def get_supported_apps(fix_only, custom_path=""):
    """Get a list of dict, a dict for each supported application."""
    database_files = []
    if len(fix_only) != 0:
        for db_file in fix_only:
            if db_file not in BLACKLIST:
                db_file = "{0}{1}.json".format(DB_FOLDER, db_file)
                if path.exists(db_file):
                    database_files.append(db_file)
    else:
        files = glob("{0}*.json".format(path.join(DB_FOLDER, "")))
        for file in files:
            if path.splitext(path.basename(file))[0] not in BLACKLIST:
                database_files.append(file)
    if len(fix_only) > 1 and custom_path:
        exit("You can't use --path with more than application at once.")
    database_files.sort()
    supported_apps = []
    for db_file in database_files:
        application_data = Parser(db_file, args)
        if application_data.is_installed():
            supported_apps.append(application_data.get_application())
    return supported_apps


def apply(is_install):
    """Fix Hardcoded Tray icons.
    Args:
        is_install(bool):
            True: To apply the modifications
            False: To revert it.
    """
    apps = get_supported_apps(args.only, args.path)
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

print("Welcome to the tray icons hardcoder fixer!")
print("Your indicator icon size is : {0}".format(args.icon_size))
print("The detected desktop environement : {0}".format(DESKTOP_ENV.title()))
if not isinstance(args.theme, dict):
    print("Your current icon theme is : {0}".format(args.theme))
else:
    print("Your current dark icon theme is : {0}".format(args.theme["dark"]))
    print("Your current light icon theme is : {0}".format(args.theme["light"]))
print("Conversion tool : {0}".format(args.svgtopng))
print("Applications will be fixed : ", end="")
print(",".join(map(lambda x: x.title(), args.only)) if args.only else "All")

choice = args.choice
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
    apply(True)
elif choice == 2:
    print("Reverting now..\n")
    apply(False)

print("\nDone, Thank you for using the Hardcode-Tray fixer!")
