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
from gettext import gettext as _
from glob import glob
from os import path

from HardcodeTray.const import DB_FOLDER
from HardcodeTray.enum import Action
from HardcodeTray.utils.cli import progress

from HardcodeTray.modules.log import Logger
from HardcodeTray.modules.parser import Parser

from HardcodeTray.modules.config.arguments import ArgumentsConfig
from HardcodeTray.modules.config.json import JSONConfig
from HardcodeTray.modules.config.system import SystemConfig

from HardcodeTray.modules.svg.svg import SVG

class App:
    """
        Main application.
    """
    _args = None  # Arguments Parser
    _json = None  # Config file (json)
    _system = None  # System config
    _svgtopng = None
    _icon_size = None
    _scaling_factor = None
    _app = None  # App Object

    def __init__(self, args):
        App._args = ArgumentsConfig(args)
        App._json = JSONConfig()
        App._system = SystemConfig()

    @staticmethod
    def set_args(args):
        """Get default instance of the app."""
        if not App._app:
            App._app = App(args)

    @staticmethod
    def get(key):
        """Return a value from Arguments, json config file, System."""
        sources = [App._args, App._json, App._system]
        value = None

        if hasattr(App, "_" + key):
            value = getattr(App, "_" + key)
            if value is not None:
                return value

        for source in sources:
            if hasattr(source, key):
                method = getattr(source, key)
                if hasattr(method, "__call__"):
                    value = method()
                    if value is not None:
                        setattr(App, "_" + key, value)
                        return value
        return None

    @staticmethod
    def get_supported_apps():
        """Get a list of dict, a dict for each supported application."""
        supported_apps = []
        files = []
        if App.get("only"):
            for db_file in App.get("only"):
                db_file = "{0}{1}.json".format(DB_FOLDER, db_file)
                if path.exists(db_file):
                    files.append(db_file)
        else:
            files = glob("{0}*.json".format(path.join(DB_FOLDER, "")))
        files.sort()

        blacklist = App.get("blacklist")
        if not blacklist:
            blacklist = []
        for db_file in files:
            db_filename = path.splitext(path.basename(db_file))[0]
            if db_filename not in blacklist:
                application_data = Parser(db_file)
                if application_data.is_installed():
                    supported_apps.append(application_data.get_application())

        return supported_apps

    @staticmethod
    def execute():
        """Fix Hardcoded Tray icons."""
        action = App.get("action")
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
            print(_("Took {:.2f}s to finish the tasks").format(total_time))
        elif action == Action.APPLY:
            print(_("No apps to fix!"))
        elif action == Action.CLEAR_CACHE:
            print(_("No cache found."))
        else:
            print(_("No apps to revert!"))

    @staticmethod
    def svg():
        """
            Return an instance of a conversion tool
        """
        if App._svgtopng is None:
            conversion_tool = App.get("conversion_tool")
            App._svgtopng = SVG.factory(App.get("colors"), conversion_tool)
        return App._svgtopng

    @staticmethod
    def icon_size():
        """
            Return the icon size.
        """
        if not App._icon_size:
            icon_size = App.get("icon_size")
            App._icon_size = icon_size
        return App._icon_size

    @staticmethod
    def scaling_factor():
        """
            Returns the scaling factor.
        """
        if not App._scaling_factor:
            scaling_factor = App.get("scaling_factor")
            if scaling_factor and scaling_factor > 1:
                # Change icon size by * it by the scaling factor
                App._icon_size = round(App.icon_size() * scaling_factor, 0)
                Logger.debug("Icon Size: {}".format(App._icon_size))
            App._scaling_factor = scaling_factor
        return App._scaling_factor

    @staticmethod
    def theme(key=None):
        """Return the icon theme instance"""
        theme = App.get("theme")
        if key and isinstance(theme, dict):
            return theme.get(key)
        return theme

    @staticmethod
    def path():
        """
            The icons path, specified per application.
        """
        path_ = App.get("path")
        if len(App.get("only")) > 1 and path_:
            exit(_("You can't use --path with more than application at once."))
        return path_
