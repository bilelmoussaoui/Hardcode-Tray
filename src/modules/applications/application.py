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
from concurrent.futures import ThreadPoolExecutor as Executor
from os import path
from shutil import rmtree
from src.const import BACKUP_FOLDER
from src.enum import Action
from src.utils import symlink_file, mchown
from src.decorators import symlinks_installer, revert_wrapper, install_wrapper
from src.modules.backup import Backup

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
        self.is_done = True
        self.parser = parser
        self._selected_backup = None
        self._back_dir = None
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
        return hasattr(self.parser, "symlinks")

    def install_symlinks(self):
        """Create symlinks for some applications files."""
        if self.has_symlinks():
            symlinks = self.symlinks
            for syml in symlinks:
                for directory in self.app_path:
                    root = symlinks[syml]["root"]
                    dest = directory.append(symlinks[syml]["dest"])
                    if path.exists(dest):
                        self.backup.create(dest)
                        symlink_file(root, dest)

    def remove_symlinks(self):
        """Remove symlinks created by the application."""
        if self.has_symlinks():
            symlinks = self.symlinks
            for syml in symlinks:
                for directory in self.app_path:
                    self.backup.remove(directory.append(symlinks[syml]["dest"]))

    def clear_cache(self):
        """Clear Backup cache."""
        backup_folder = path.join(BACKUP_FOLDER, self.name, "")
        if path.exists(backup_folder):
            rmtree(backup_folder)
            return True
        return False

    def execute(self, action):
        """Execute actions: Apply/Revert."""
        for icon_path in self.icons_path:
            with Executor(max_workers=4) as exe:
                for icon in self.icons:
                    if action == Action.APPLY:
                        exe.submit(self.install_icon, icon, icon_path)
                    elif action == Action.REVERT:
                        exe.submit(self.revert_icon, icon, icon_path)

    @install_wrapper
    def install(self):
        """Install the application icons."""
        self.execute(Action.APPLY)

    @revert_wrapper
    def reinstall(self):
        """Reinstall the application icons and remove symlinks."""
        self.execute(Action.REVERT)

    @symlinks_installer
    def install_icon(self, icon, icon_path):
        """Install icon to the current directory."""
        ext_orig = icon.orig_ext
        theme_icon = icon.theme
        ext_theme = icon.theme_ext
        icon_size = icon.icon_size
        output_icon = icon_path.append(icon.original)
        if not self.backup_ignore:
            self.backup.create(output_icon)
        if ext_theme == ext_orig:
            symlink_file(theme_icon, output_icon)
        elif ext_theme == "svg" and ext_orig == "png":
            from src.app import App
            App.svg().to_png(theme_icon, output_icon, icon_size)
            mchown(output_icon)

    def revert_icon(self, icon, icon_path):
        """Revert to the original icon."""
        output_icon = icon_path.append(icon.original)
        if not self.backup_ignore:
            self.backup.remove(output_icon)
