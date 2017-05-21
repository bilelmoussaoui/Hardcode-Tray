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
from os import path
from shutil import rmtree
from src.const import BACKUP_FOLDER
from src.utils import backup, revert, symlink_file, mchown
from src.decorators import symlinks_installer, revert_wrapper, install_wrapper


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
    def backup_dir(self):
        """Return the backup directory of the current application."""
        return self._back_dir

    @backup_dir.setter
    def backup_dir(self, backup_dir):
        self._back_dir = backup_dir

    @property
    def selected_backup(self):
        """Return the selected backup directory during the revert process."""
        return self._selected_backup

    @selected_backup.setter
    def selected_backup(self, selected_backup):
        if path.exists(selected_backup):
            self._selected_backup = selected_backup
        else:
            raise FileNotFoundError

    @property
    def icons_path(self):
        """Return the application installation paths."""
        return self.parser.icons_path

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
                    backup(self.backup_dir, dest)
                    symlink_file(root, dest)

    def remove_symlinks(self):
        """Remove symlinks created by the application."""
        if self.has_symlinks():
            symlinks = self.symlinks
            for syml in symlinks:
                for directory in self.app_path:
                    revert(self.name, self.selected_backup,
                           directory.append(symlinks[syml]["dest"]))

    def clear_cache(self):
        """Clear Backup cache."""
        backup_folder = path.join(BACKUP_FOLDER, self.name, "")
        if path.exists(backup_folder):
            rmtree(backup_folder)
            return True
        return False

    def get_output_icons(self):
        """Return a list of output icons."""
        icons = []
        for icon in self.icons:
            for icon_path in self.icons_path:
                output_icon = icon_path.append(icon.original)
                icons.append({
                    "output_icon": output_icon,
                    "data": icon,
                    "path": icon_path
                })
        return icons

    @install_wrapper
    def install(self):
        """Install the application icons."""
        for icon in self.get_output_icons():
            if not self.parser.backup_ignore:
                backup(self.backup_dir, icon["output_icon"])
            self.install_icon(icon["data"], icon["path"])

    @revert_wrapper
    def reinstall(self):
        """Reinstall the application icons and remove symlinks."""
        for icon in self.get_output_icons():
            if not self.parser.backup_ignore:
                revert(self.name,
                       self.selected_backup,
                       icon["output_icon"])

    @symlinks_installer
    def install_icon(self, icon, icon_path):
        """Install icon to the current directory."""
        ext_orig = icon.orig_ext
        theme_icon = icon.theme
        ext_theme = icon.theme_ext
        icon_size = icon.icon_size
        output_icon = icon_path.append(icon.original)
        if ext_theme == ext_orig:
            symlink_file(theme_icon, output_icon)
        elif ext_theme == "svg" and ext_orig == "png":
            from src.app import App
            App.svg().to_png(theme_icon, output_icon, icon_size)
            mchown(output_icon)
