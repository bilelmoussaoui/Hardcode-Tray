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
from src.utils import symlink_file, get_extension


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
            output_icon = picon_path + icon.original
            if not get_extension(output_icon):
                output_icon += ".{0}".format(icon.theme_ext)

            for symlink_icon in icon.symlinks:
                symlink_icon = icon_path + symlink_icon
                if not get_extension(symlink_icon):
                    symlink_icon += ".{0}".format(icon.theme_ext)
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
        if (not app.backup_ignore and
                not App.config().get("backup-ignore", False)):
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
        if app.BACKUP_IGNORE or app.backup_ignore:
            app.remove_symlinks()
            func(app)
        else:
            app.backup.select()
            if app.backup.selected_backup:
                app.remove_symlinks()
                func(app)
            else:
                app.is_done = False
    return wrapper
