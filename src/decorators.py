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
from os import path

from src.utils import symlink_file


def symlinks_installer(func):
    """
        Symlinks installation decorator
    """
    def wrapper(application, icon, icon_path):
        """
            Install symlinks easily.
        """
        func(application, icon, icon_path)

        if icon.has_symlinks():
            output_icon = path.join(str(icon_path), icon.original)
            for symlink_icon in icon.symlinks:
                symlink_icon = path.join(str(icon_path), symlink_icon)
                symlink_file(output_icon, symlink_icon)

    return wrapper


def install_wrapper(func):
    """
        Install decorator
    """
    def wrapper(app):
        """
        Create backup file and apply the modifications.
        """
        from src.app import App
        if not app.backup_ignore and not App.get("backup_ignore"):
            app.backup.create_backup_dir()

        app.install_symlinks()
        func(app)
    return wrapper


def revert_wrapper(func):
    """
        Revert decorator
    """
    def wrapper(app):
        """
            Revert to the old version and remove symlinks.
        """
        if app.BACKUP_IGNORE or app.backup_ignore or App.get("backup_ignore"):
            app.remove_symlinks()
            func(app)
        else:
            app.backup.select()
            if app.backup.selected_backup:
                app.remove_symlinks()
                func(app)
            else:
                app.success = False
    return wrapper
