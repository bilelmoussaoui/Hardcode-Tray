#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.7
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
from os import geteuid
from argparse import ArgumentParser
from src.utils import get_list_of_themes
from src.const import DESKTOP_ENV
from src.enum import Action, ConversionTools
from src.app import App

if geteuid() != 0:
    exit("You need to have root privileges to run the script.\
        \nPlease try again, this time using 'sudo'. Exiting.")

parser = ArgumentParser(prog="hardcode-tray")
THEMES_LIST = get_list_of_themes()
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
                    type=str, choices=ConversionTools.choices())
parser.add_argument('--change-color', "-cc", type=str, nargs='+',
                    help="Replace a color with an other one, "
                    "works only with SVG.")
parser.add_argument("--clear-cache", action="store_true",
                    help="Clear backup files")
args = parser.parse_args()
hardcode_tray = App.get_default(args)

if (not DESKTOP_ENV or DESKTOP_ENV == "other") and not App.icon_size():
    exit("You need to run the script using 'sudo -E'.\nPlease try again")

print("Welcome to the tray icons hardcoder fixer!")
print("Your indicator icon size is : {0}".format(App.icon_size()))
print("The detected desktop environement : {0}".format(DESKTOP_ENV.title()))
if not isinstance(App.theme(), dict):
    print("Your current icon theme is : {0}".format(App.theme()))
else:
    print("Your current dark icon theme is : {0}".format(App.theme()["dark"]))
    print("Your current light icon theme is : {0}".format(App.theme()["light"]))
print("Conversion tool : {0}".format(App.svg()))
print("Applications will be fixed : ", end="")
print(",".join(map(lambda x: x.title(), App.only())) if App.only() else "All")

# Clear backup cache
action = App.action()
if not action:
    print("1 - Apply")
    print("2 - Revert")
    print("3 - Clear Backup Cache")
    has_chosen = False
    while not has_chosen:
        try:
            action = int(input("Please choose: "))
            if action not in [1, 2, 3]:
                print("Please try again")
            else:
                has_chosen = True
        except ValueError:
            print("Please choose a valid value!")
        except KeyboardInterrupt:
            exit("")

if action == Action.APPLY:
    print("Applying now..\n")
elif action == Action.REVERT:
    print("Reverting now..\n")
elif action == Action.CLEAR_CACHE:
    print("Clearing cache...\n")

hardcode_tray.execute(action)

print("\nDone, Thank you for using the Hardcode-Tray fixer!")
