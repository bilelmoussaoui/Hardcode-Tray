#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.8
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
from os import path
from shutil import rmtree
from time import time

from concurrent.futures import ThreadPoolExecutor as Executor
from src.decorators import install_wrapper, revert_wrapper, symlinks_installer
from src.enum import Action
from src.modules.backup import Backup
from src.utils import mchown, symlink_file


class Application:
    """Application class."""
    BACKUP_IGNORE = False

    def __init__(self, parser):
        """
        Init method.

        @json_file(str): the json database file name
        @custom_path(str): used when the application is compiled
                    and installed in an other customn path
        """
        self.success = True
        self.parser = parser
        self.backup = Backup(self)

    @property
    def name(self):
        """Return the application name."""
        return self.parser.name

    @property
    def icons(self):
        """Return the application icons."""
        return self.parser.icons

    @property
    def app_path(self):
        """Return the application installation paths."""
        return self.parser.app_path

    @property
    def icons_path(self):
        """Return the application installation paths."""
        return self.parser.icons_path

    @property
    def backup_ignore(self):
        """Return either the backup files should be created or not."""
        return self.parser.backup_ignore

    @property
    def symlinks(self):
        """Return application symlinks."""
        return self.parser.symlinks

    def has_symlinks(self):
        """Return a boolean value if either the application have symlinks."""
        symlinks_found = hasattr(self.parser, "symlinks") and self.symlinks
        return symlinks_found

    def install_symlinks(self):
        """Create symlinks for some applications files."""
        if self.has_symlinks():
            for app_path in self.app_path:
                for symlink in self.symlinks.values():
                    root = symlink["root"]
                    dest = app_path + symlink["dest"]
                    if path.exists(dest):
                        self.backup.create(dest)
                        symlink_file(root, dest)

    def remove_symlinks(self):
        """Remove symlinks created by the application."""
        if self.has_symlinks():
            for app_path in self.app_path:
                for symlink in self.symlinks.values():
                    self.backup.remove(app_path + symlink["dest"])

    def clear_cache(self):
        """Clear Backup cache."""
        backup_folder = self.backup.get_folder()

        if path.exists(backup_folder):
            rmtree(backup_folder)
            self.success = True
        else:
            self.success = False

    @install_wrapper
    def install(self):
        """Install the application icons."""
        self.execute(Action.APPLY)

    @revert_wrapper
    def reinstall(self):
        """Reinstall the application icons and remove symlinks."""
        self.execute(Action.REVERT)

    def execute(self, action):
        """Execute actions: Apply/Revert."""
        for icon_path in self.icons_path:
            with Executor(max_workers=4) as exe:
                for icon in self.icons:
                    if action == Action.APPLY:
                        exe.submit(self.install_icon, icon, icon_path)
                    elif action == Action.REVERT:
                        exe.submit(self.revert_icon, icon, icon_path)

    def do_action(self, action):
        """Execute an action, and return the time it took."""
        start_time = time()
        if action == Action.APPLY:
            self.install()
        elif action == Action.REVERT:
            self.reinstall()
        elif action == Action.CLEAR_CACHE:
            self.clear_cache()

        return time() - start_time


    @symlinks_installer
    def install_icon(self, icon, icon_path):
        """Install icon to the current directory."""
        ext_orig = icon.orig_ext
        theme_icon = icon.theme
        ext_theme = icon.theme_ext
        icon_size = icon.icon_size
        output_icon = icon_path + icon.original

        # Backup the output_icon
        if not self.backup_ignore:
            self.backup.create(output_icon)

        if ext_theme == ext_orig:
            symlink_file(theme_icon, output_icon)
        elif ext_theme == "svg" and ext_orig == "png":
            from src.app import App
            if icon_size != App.icon_size():
                App.svg().to_png(theme_icon, output_icon, App.icon_size())
            else:
                App.svg().to_png(theme_icon, output_icon)

            mchown(output_icon)

    def revert_icon(self, icon, icon_path):
        """Revert to the original icon."""
        output_icon = icon_path + icon.original
        # Revert to the original icon
        if not self.backup_ignore:
            self.backup.remove(output_icon)
