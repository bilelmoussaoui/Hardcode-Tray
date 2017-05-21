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
from .utils import symlink_file, show_select_backup, create_backup_dir


def symlinks_installer(func):
    def wrapper(application, icon, icon_path):
        cname = application.__class__.__name__
        func(application, icon, icon_path)
        if icon.has_symlinks():
            output_icon = icon_path.append(icon.original)
            for symlink_icon in icon.symlinks:
                if cname != "Application":
                    symlink_icon = '{0}.{1}'.format(
                        icon_path.append(symlink_icon),
                        icon.theme_ext)
                else:
                    symlink_icon = icon_path.append(symlink_icon)
                symlink_file(output_icon, symlink_icon)
    return wrapper


def install_wrapper(func):
    def wrapper(app):
        app.backup_dir = create_backup_dir(app.name)
        app.install_symlinks()
        func(app)
    return wrapper


def revert_wrapper(func):
    def wrapper(application):
        if application.BACKUP_IGNORE:
            application.remove_symlinks()
            func(application)
        else:
            application.selected_backup = show_select_backup(application.name)
            if application.selected_backup:
                application.remove_symlinks()
                func(application)
            else:
                application.is_done = False
    return wrapper
