#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
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
from glob import glob
from json import load
from os import path

from gi.repository import Gio

from src.const import CONFIG_FILE, DB_FOLDER, DESKTOP_ENV
from src.enum import Action, ConversionTools
from src.modules.log import Logger
from src.modules.parser import Parser
from src.modules.svg import *
from src.modules.theme import Theme
from src.utils import get_scaling_factor, progress, replace_to_6hex


class App:
    """
        Main application.
    """
    _args = None  # Arguments Parser
    _config = None  # Config file (json)
    _theme = None  # Theme object
    _size = None  # Icon size
    _scaling_factor = -1  # Scaling factor
    _action = None  # Action.APPLY/Action.REVERT/Action.CLEAR_CACHE
    _only = []  # Fix only list of apps
    _path = None  # App path to use with fix only
    _colors = []  # Colors
    _svgtopng = None

    _app = None  # App Object

    def __init__(self, args):
        App._args = args

    @staticmethod
    def get_default(args=None):
        """Return the default instance of App."""
        if App._app is None:
            App._app = App(args)
        return App._app

    @staticmethod
    def get_supported_apps():
        """Get a list of dict, a dict for each supported application."""
        database_files = []
        if App.only():
            for db_file in App.only():
                db_file = "{0}{1}.json".format(DB_FOLDER, db_file)
                if path.exists(db_file):
                    database_files.append(db_file)
        else:
            blacklist = App.config().get("blacklist", [])
            files = glob("{0}*.json".format(path.join(DB_FOLDER, "")))

            for file_ in files:
                if path.splitext(path.basename(file_))[0] not in blacklist:
                    database_files.append(file_)

        database_files.sort()
        supported_apps = []

        for db_file in database_files:
            application_data = Parser(db_file)
            if application_data.is_installed():
                supported_apps.append(application_data.get_application())

        return supported_apps

    @staticmethod
    def execute():
        """Fix Hardcoded Tray icons."""
        action = App.action()
        apps = App.get_supported_apps()
        done = []
        total_time = 0
        counter = 0
        total_counter = len(apps)
        for app in apps:
            app_name = app.name

            delta = app.do_action(action)

            total_time += delta
            if app.success:
                counter += 1
                if app_name not in done:
                    progress(counter, total_counter, delta, app_name)
                    done.append(app_name)
            else:
                total_counter -= 1

        if apps:
            print("Took {:.2f}s to finish the tasks".format(total_time))
        elif action == Action.APPLY:
            print("No apps to fix! Please report on GitHub if this is not the case")
        elif action == Action.CLEAR_CACHE:
            print("No cache found.")
        else:
            print("No apps to revert!")

    @staticmethod
    def args():
        """
            Application arguments
        """
        return App._args

    @staticmethod
    def config():
        """
            json config file content.
        """
        if App._config is None:
            config = {}
            if path.isfile(CONFIG_FILE):
                Logger.debug("Reading config file: {}".format(CONFIG_FILE))
                with open(CONFIG_FILE, 'r') as data:
                    try:
                        config = load(data)
                    except ValueError:
                        Logger.warning("The config file is "
                                       "not a valid json file.")
            App._config = config
        return App._config

    @staticmethod
    def svg():
        """
            Return an instance of a conversion tool
        """
        if App._svgtopng is None:
            conversion_tool = None
            # Read default config/arguments parser
            if App.args().conversion_tool:
                conversion_tool = App.args().conversion_tool
                Logger.debug("Arguments/Conversion Tool: {}".format(conversion_tool))
            elif App.config().get("conversion-tool"):
                conversion_tool = App.config().get("conversion-tool")
                Logger.debug("Config/Conversion Tool: {}".format(conversion_tool))

            if conversion_tool:
                try:
                    App._svgtopng = globals()[conversion_tool](App.colors())
                except SVGNotInstalled:
                    exit("The selected conversion tool is not installed.")
            else:
                svgtool_found = False
                for conversion_tool in ConversionTools.choices():
                    try:
                        App._svgtopng = globals()[conversion_tool](App.colors())
                        svgtool_found = True
                        break
                    except SVGNotInstalled:
                        svgtool_found = False

                if not svgtool_found:
                    raise SVGNotInstalled
        return App._svgtopng

    @staticmethod
    def icon_size():
        """
            Return the icon size.
        """
        if App._size is None:
            if App.args().size:
                App._size = App.args().size
                Logger.debug("Arguments/Icon Size: {}".format(App._size))
            else:
                App._size = int(App.config().get("icons", {}).get("size", 0))
                if App._size not in [16, 22, 24]:
                    if DESKTOP_ENV in ("pantheon", "xfce"):
                        App._size = 24
                    else:
                        App._size = 22
                    Logger.warning("Icon size in the config file is wrong."
                                   "Falling back to the detected one...")
                    Logger.debug("Detected Icon Size: {}".format(App._size))
                else:
                    Logger.debug("Config/Icon Size: {}".format(App._size))
        return App._size

    @staticmethod
    def scaling_factor():
        """
            Returns the scaling factor.
        """
        if App._scaling_factor == -1:
            scaling_factor = get_scaling_factor(DESKTOP_ENV)
            App._scaling_factor = scaling_factor
            if scaling_factor > 1:
                # Change icon size by * it by the scaling factor
                App._size = round(App.icon_size() * scaling_factor, 0)
                Logger.debug("Icon Size: {}".format(App._size))
        return App._scaling_factor

    @staticmethod
    def theme(dark_theme=None):
        """
            Theme instance.
        """
        if App._theme is None:
            # If the theme was sepecified on args
            if App.args().theme:
                App._theme = Theme(App.args().theme)
                Logger.debug("Arguments/Theme: {}".format(App._theme))
            elif App.args().light_theme and App.args().dark_theme:
                App._theme = {
                    "dark": Theme(App.args().dark_theme),
                    "light": Theme(App.args().light_theme)
                }
                Logger.debug("Arguments/Dark Theme: {}".format(App.args().dark_theme))
                Logger.debug("Arguments/Light Theme: {}".format(App.args().light_theme))

            # Or on the config file
            elif App.config().get("icons"):
                theme = App.config()["icons"].get("theme", {})
                if isinstance(theme, str):
                    App._theme = Theme(theme)
                    Logger.debug("Config/Theme: {}".format(theme))
                else:
                    if theme.get("light") and theme.get("dark"):
                        App._theme = {
                            "dark": Theme(theme["dark"]),
                            "light": Theme(theme["light"])
                        }
                        Logger.debug("Config/Dark Theme: {}".format(theme.get("dark")))
                        Logger.debug("Config/Light Theme: {}".format(theme.get("light")))
            # Fallback to system theme
            if not App._theme:
                source = Gio.SettingsSchemaSource.get_default()
                if source.lookup("org.gnome.desktop.interface", True):
                    gsettings = Gio.Settings.new("org.gnome.desktop.interface")
                    theme_name = gsettings.get_string("icon-theme")
                    App._theme = Theme(theme_name)
                    Logger.debug("System/Theme: {}".format(theme_name))
                else:
                    Logger.error("System/Theme: Not detected.")

        if dark_theme and isinstance(App._theme, dict):
            return App._theme[dark_theme]
        return App._theme

    @staticmethod
    def colors():
        """
            List of colors to be replaced with new ones.
        """
        if App.args().change_color and not App._colors:
            colors = []
            for color in App.args().change_color:
                color = color.strip().split(" ")
                to_replace = replace_to_6hex(color[0])
                for_replace = replace_to_6hex(color[1])
                colors.append([to_replace, for_replace])
            App._colors = colors
        return App._colors

    @staticmethod
    def action():
        """
            Which action should be done?
        """
        if App._action is None:
            # Can't use apply and revert action on the same time
            if App.args().apply and App.args().revert:
                raise ValueError
            # Can't apply/revert and clear cache on the same time
            elif (App.args().apply or App.args().revert) and App.args().clear_cache:
                raise ValueError
            elif App.args().apply:
                App._action = Action.APPLY
            elif App.args().revert:
                App._action = Action.REVERT
            elif App.args().clear_cache:
                App._action = Action.CLEAR_CACHE
            else:
                print("1 - Apply")
                print("2 - Revert")
                print("3 - Clear Backup Cache")
                has_chosen = False
                while not has_chosen:
                    try:
                        action = int(input("Please choose: "))
                        if action not in Action.choices():
                            print("Please try again")
                        else:
                            has_chosen = True
                            App._action = action
                    except ValueError:
                        print("Please choose a valid value!")
                    except KeyboardInterrupt:
                        exit("")
        return App._action

    @staticmethod
    def only():
        """
            List of applications to be fixed.
        """
        if not App._only and App.args().only:
            only = App.args().only.lower().strip().split(",")
            for bfile in App.config().get("blacklist", []):
                only.remove(bfile)
            App._only = only
        return App._only

    @staticmethod
    def path():
        """
            The icons path, specified per application.
        """
        if App.args().path and App.only():
            proposed_path = App.args().path
            if path.exists(proposed_path) and path.isdir(proposed_path):
                App._path = proposed_path
            else:
                raise FileNotFoundError("Please select a valid --path")
        if len(App.only()) > 1 and App._path:
            exit("You can't use --path with more than application at once.")
        return App._path
