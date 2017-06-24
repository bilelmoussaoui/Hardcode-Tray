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
from gettext import gettext as _
from os import path, remove
from shutil import rmtree
from time import time

from HardcodeTray.const import BACKUP_FOLDER
from HardcodeTray.decorators import install_wrapper, revert_wrapper, symlinks_installer
from HardcodeTray.enum import Action
from HardcodeTray.modules.backup import Backup
from HardcodeTray.modules.log import Logger
from HardcodeTray.utils import mchown, symlink_file


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

    def __getattr__(self, name):
        if hasattr(self.parser, name):
            return getattr(self.parser, name)
        elif hasattr(self, name):
            return getattr(self, name)
        Logger.warning("Couldn't find attribute {}".format(name))
        return None

    def has_symlinks(self):
        """Return a boolean value if either the application have symlinks."""
        return hasattr(self.parser, "symlinks")

    def install_symlinks(self):
        """Create symlinks for some applications files."""
        if self.has_symlinks():
            for app_path in self.app_path:
                for symlink in self.symlinks.values():
                    root = symlink["root"]
                    dest = path.join(str(app_path), symlink["dest"])
                    if path.exists(dest):
                        self.backup.create(dest)
                        symlink_file(root, dest)

    def remove_symlinks(self):
        """Remove symlinks created by the application."""
        if self.has_symlinks():
            for app_path in self.app_path:
                for symlink in self.symlinks.values():
                    symlink = path.join(str(app_path), symlink["dest"])
                    self.backup.remove(symlink)

    def clear_cache(self):
        """Clear Backup cache."""
        backup_folder = path.join(BACKUP_FOLDER, self.name, "")
        Logger.debug("Clearing cache of: {}".format(self.name))

        if path.exists(backup_folder):
            rmtree(backup_folder)
            Logger.debug("Cache cleaned.")
        else:
            Logger.debug("Cache not found.")
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
            for icon in self.icons:
                if action == Action.APPLY:
                    self.install_icon(icon, icon_path)
                elif action == Action.REVERT:
                    self.revert_icon(icon, icon_path)

    @symlinks_installer
    def install_icon(self, icon, icon_path):
        """Install icon to the current directory."""
        ext_orig = icon.orig_ext
        theme_icon = icon.theme
        ext_theme = icon.theme_ext
        icon_size = icon.icon_size
        output_icon = path.join(str(icon_path), icon.original)

        # Backup the output_icon
        if not self.backup_ignore:
            self.backup.create(output_icon)

        if ext_theme == ext_orig and theme_icon != output_icon:
            symlink_file(theme_icon, output_icon)
        elif ext_theme == "svg" and ext_orig == "png":
            from HardcodeTray.app import App
            if icon_size != App.icon_size():
                App.svg().to_png(theme_icon, output_icon, App.icon_size())
            else:
                App.svg().to_png(theme_icon, output_icon)

            mchown(output_icon)

    def revert_icon(self, icon, icon_path):
        """Revert to the original icon."""
        output_icon = path.join(str(icon_path), icon.original)
        # Revert to the original icon
        if not self.backup_ignore:
            self.backup.remove(output_icon)
        else:
            remove(output_icon)

    def do_action(self, action):
        """Do an action, return the time it took."""
        start_time = time()

        if action == Action.APPLY:
            self.install()
            if not self.success:
                print(_("Failed to fix {}").format(self.name))

        elif action == Action.REVERT:
            self.reinstall()
            if not self.success and self.backup.exists:
                print(_("Couldn't revert to those icons :("))

        elif action == Action.CLEAR_CACHE:
            self.clear_cache()
            if not self.success:
                print(_("No backup found for {}").format(self.name))

        return time() - start_time
