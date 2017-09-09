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

from HardcodeTray.const import DB_FOLDER, USERHOME
from HardcodeTray.enum import Action
from HardcodeTray.utils.cli import progress

from HardcodeTray.parser import Parser
from HardcodeTray.config import Config

from HardcodeTray.svg import SVG


class App:
    """
        Main application.
    """
    instance = None

    def __init__(self, args):
        self.config = Config(args)
        self.parser = Parser()
        # Default instance of an svg to png converter
        self.svg = None
        self.init()

    def init(self):
        """Init some important objects like SVG;"""
        conversion_tool = self.config.get("conversion_tool")
        colors = self.config.get("colors")
        self.svg = SVG.factory(colors, conversion_tool)
        self.parser.register_callback(
            r'\{userhome\}', lambda key, path: path.replace(key, USERHOME)
        )
        self.parser.register_callback(
            r'\{size\}', lambda key, path: path.replace(key, self.config.get("icon_size"))
        )
        self.parser.register_callback(
            r'\{dropbox\}', lambda key, path: path.replace(
                key, "dropbox-lnx.x86_64-34.3.18")
        )
        App.instance = self

    @staticmethod
    def get_default():
        """Return default instance of the app."""
        return App.instance

    def list_apps(self):
        """Return a list apps to fix."""
        files = []
        if self.config.get("only"):
            for db_file in self.config.get("only"):
                db_file = "{0}{1}.json".format(DB_FOLDER, db_file)
                if path.exists(db_file):
                    files.append(db_file)
        else:
            files = glob("{0}*.json".format(path.join(DB_FOLDER, "")))
        files.sort()
        return files

    def get_supported_apps(self):
        """Get a list of dict, a dict for each supported application."""
        # List of supported apps by your current theme/installed
        apps = []
        db_files = self.list_apps()
        blacklist = self.config.get("blacklist")

        for db_file in db_files:
            db_filename = path.splitext(path.basename(db_file))[0]
            if db_filename not in blacklist:
                db = self.parser.parse(db_file)
                if db.is_installed:
                    # Create an application instance
                    # From a database
                    app = db.factory()
                    print(app)
                    apps.append(app)
        return apps

    def execute(self):
        """Fix Hardcoded Tray icons."""
        action = self.config.get("action")
        apps = self.get_supported_apps()
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
