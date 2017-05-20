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
from json import load
from os import path
from .modules.parser import Parser
from .modules.theme import Theme
from .modules.svg.svg import SVGNotInstalled
from .const import DESKTOP_ENV, CONFIG_FILE, DB_FOLDER
from .enum import CONVERSION_TOOLS, Action


class App:
    _args = None  # Arguments Parser
    _config = None  # Config file (json)
    _log = None  # Logger
    _svgtopng = None  # Svg to png object
    _theme = None  # Theme object
    _size = None  # Icon size
    _scaling_factor = -1  # Scaling factor
    _action = None  # Action.APPLY/Action.REVERT/Action.CLEAR_CACHE
    _only = []  # Fix only list of apps
    _path = None  # App path to use with fix only
    _colors = []  # Colors

    _app = None # App Object

    def __init__(self, args):
        App._args = args

    @staticmethod
    def get_default(args = None):
        if App._app == None:
              App._app = App(args)
        return App._app


    def get_supported_apps(self):
        """Get a list of dict, a dict for each supported application."""
        database_files = []
        if len(App.only()) != 0:
            blacklist = App.config().get("blacklist", [])
            for db_file in App.only():
                if db_file not in blacklist:
                    db_file = "{0}{1}.json".format(DB_FOLDER, db_file)
                    if path.exists(db_file):
                        database_files.append(db_file)
        else:
            files = glob("{0}*.json".format(path.join(DB_FOLDER, "")))
            for file in files:
                if path.splitext(path.basename(file))[0] not in BLACKLIST:
                    database_files.append(file)
        database_files.sort()
        supported_apps = []
        for db_file in database_files:
            application_data = Parser(db_file)
            if application_data.is_installed():
                supported_apps.append(application_data.get_application())
        return supported_apps

    def execute(self, action):
        """Fix Hardcoded Tray icons.
            Args:
                action(Action):
                    APPLY: To apply the modifications
                    REVERT: To revert it.
        """
        apps = self.get_supported_apps()
        done = []
        if len(apps) != 0:
            cnt = 0
            counter_total = sum(app.data.supported_icons_cnt for app in apps)
            for i, app in enumerate(apps):
                app_name = app.name
                if action == Action.APPLY:
                    app.install()
                elif action == Action.REVERT:
                    app.reinstall()
                elif action == Action.CLEAR_CACHE:
                    app.clear_cache()
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
            if action == Action.APPLY:
                exit("No apps to fix! Please report on GitHub if this is not the case")
            else:
                exit("No apps to revert!")

    def log():
        if App._log == None:
            logger = logging.getLogger('hardcode-tray')
            tmp_file = '/tmp/Hardcode-Tray/-{0}.log'.format(
                strftime(LOG_FILE_FORMAT))
            if not path.exists(path.dirname(tmp_file)):
                makedirs(path.dirname(tmp_file))
            if not path.exists(tmp_file):
                f = open(tmp_file, 'w')
                f.write('')
                f.close()
            handler = logging.FileHandler(tmp_file)
            formater = logging.Formatter(
                '[%(levelname)s] - %(asctime)s - %(message)s')
            handler.setFormatter(formater)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
            App._log = logging.getLogger("hardcode-tray")
        return App._log

    def svgtopng():
        if App._svgtopng == None:
            if App.args().conversion_tool:
                conversion_tool = App.args().conversion_tool
            elif App.config().get("conversion-tool"):
                conversion_tool = App.config().get("conversion-tool")
            if conversion_tool:
                try:
                    App._svgtopng = CONVERSION_TOOLS[conversion_tool](
                        App.colors)
                except SVGNotInstalled:
                    exit("The selected conversion tool is not installed.")
            else:
                svgtool_found = False
                for conversion_tool in CONVERSION_TOOLS:
                    try:
                        App._svgtopng = CONVERSION_TOOLS[
                            conversion_tool](App.colors)
                        svgtool_found = True
                        break
                    except SVGNotInstalled:
                        svgtool_found = False

                if not svgtool_found:
                    raise SVGNotInstalled
        return App._svgtopng

    def args():
        return App._args

    def config():
        if App._config == None:
            if path.isfile(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as data:
                    App._config = load(data)
                data.close()
            else:
                App._config = {}
        return App._config

    def icon_size():
        if App._size == None:
            if App.args().size:
                App._size = App.args().size
            else:
                if DESKTOP_ENV in ("pantheon", "xfce"):
                    icon_size = 24
                else:
                    icon_size = 22
                if App.config().get("icons"):
                    App._size = App.config()["icons"].get("size", icon_size)
                    if App._size not in [16, 22, 24]:
                        App._size = icon_size
                        App.log.debug("Icon size in the config file is wrong. "
                                      "Falling back to the detected one...")
                else:
                    App._size = icon_size
        return App._size

    def scaling_factor():
        if App._scaling_factor == -1:
            scaling_factor = get_scaling_factor(DESKTOP_ENV)
            App._scaling_factor = scaling_factor
            if scaling_factor > 1:
                # Change icon size by * it by the scaling factor
                App._size = round(App.size * scaling_factor, 0)
                App.log.debug("Icon size was changed to : %s", App.size)
        return App._scaling_factor

    def theme():
        if App._theme == None:
            # If the theme was sepecified on args
            if App.args().theme:
                App._theme = Theme(App.args().theme)
            elif App.args().light_theme and App.args().dark_theme:
                App._theme = {
                    "dark": Theme(App.args().dark_theme),
                    "light": Theme(App.args().light_theme)
                }
            # Or on the config file
            elif App.config().get("icons"):
                theme = App.config()["icons"].get("theme", {})
                if isinstance(theme, str):
                    App._theme = Theme(theme)
                else:
                    if theme.get("light") and theme.get("dark"):
                        App._theme = {
                            "dark": Theme(theme["dark"]),
                            "light": Theme(theme["light"])
                        }
            # Fallback to system theme
            if not App._theme:
                source = Gio.SettingsSchemaSource.get_default()
                if source.lookup("org.gnome.desktop.interface", True):
                    gsettings = Gio.Settings.new("org.gnome.desktop.interface")
                    theme_name = gsettings.get_string("icon-theme")
                    App._theme = Theme(theme_name)
        return App._theme

    def colors():
        if App.args().change_color and not App._colors:
            colors = []
            for color in App.args().change_color:
                color = color.strip().split(" ")
                to_replace = replace_to_6hex(color[0])
                for_replace = replace_to_6hex(color[1])
                colors.append([to_replace, for_replace])
            App._colors = colors

    def action():
        if App._action == None:
            # Can't use apply and revert action on the same time
            if App.args().apply and App.args().revert:
                raise ValueError
            # Can't apply/revert and clear cache on the same time
            elif (App.args().apply or App.args().revert) and App.args().clear_cache:
                raise ValueError
            else:
                if App.args().apply:
                    App._action = Action.APPLY
                elif App.args().revert:
                    App._action = Action.REVERT
                elif App.args().clear_cache:
                    App._action = Action.CLEAR_CACHE
        return App._action

    def only():
        if not App._only and App.args().only:
            only = App.args().only.lower().strip().split(",")
            for bfile in App.config().get("blacklist", []):
                only.remove(bfile)
            App._only = only
        return App._only

    def path():
        if App.args().path and len(App.only) != 0:
            proposed_path = App.args().path
            if path.exists(proposed_path) and path.isdir(proposed_path):
                App._path = proposed_path
            else:
                raise FileNotFoundError("Please select a valid --path")
        if len(App.only()) > 1 and App._path:
            exit("You can't use --path with more than application at once.")
        return App._path
