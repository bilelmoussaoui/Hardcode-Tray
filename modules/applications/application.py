#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.6.4
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
from modules.utils import backup, revert, symlink_file, mchown, show_select_backup, create_backup_dir


class Application:
    """Application class."""

    def __init__(self, application_data, svgtopng):
        """
        Init method.

        @json_file(str): the json database file name
        @custom_path(str): used when the application is compiled
                    and installed in an other customn path
        """
        self.is_done = True
        self.svgtopng = svgtopng
        self.data = application_data

    def get_name(self):
        """Return the application name."""
        return self.data.data["name"]

    def get_icons(self):
        """Return the application icons."""
        return self.data.data["icons"]

    def get_app_paths(self):
        """Return the application installation paths."""
        return self.data.data["app_path"]

    def get_icons_path(self):
        """Return the application installation paths."""
        return self.data.data["icons_path"]

    def get_symlinks(self):
        """Return application symlinks."""
        return self.data.data["symlinks"]

    def has_symlinks(self):
        """Return a boolean value if either the application have symlinks."""
        return "symlinks" in self.data.data.keys()

    def install_symlinks(self, back_dir):
        """Create symlinks for some applications files."""
        if self.has_symlinks():
            symlinks = self.get_symlinks()
            for syml in symlinks:
                for d in self.get_app_paths():
                    root = symlinks[syml]["root"]
                    dest = d + symlinks[syml]["dest"]
                    backup(back_dir, dest)
                    symlink_file(root, dest)

    def remove_symlinks(self, selected_backup):
        """Remove symlinks created by the application."""
        if self.has_symlinks():
            symlinks = self.get_symlinks()
            for syml in symlinks:
                for d in self.get_app_paths():
                    revert(self.get_name(), selected_backup, d + symlinks[syml]["dest"])

    def get_output_icons(self):
        """Return a list of output icons."""
        icons = []
        for icon in self.get_icons():
            base_icon = icon["original"]
            for icon_path in self.get_icons_path():
                output_icon = icon_path + base_icon
                icons.append({
                    "output_icon": output_icon,
                    "data": icon,
                    "path": icon_path
                })
        return icons

    def install(self):
        """Install the application icons."""
        back_dir = create_backup_dir(self.get_name())
        self.install_symlinks(back_dir)
        for icon in self.get_output_icons():
            if not self.data.data["backup_ignore"]:
                backup(back_dir, icon["output_icon"])
            self.install_icon(icon["data"], icon["path"])

    def reinstall(self):
        """Reinstall the application icons and remove symlinks."""
        selected_backup = show_select_backup(self.get_name())
        if selected_backup:
            self.remove_symlinks(selected_backup)
            for icon in self.get_output_icons():
                if not self.data.data["backup_ignore"]:
                    revert(self.get_name(), selected_backup, icon["output_icon"])
        else:
            self.is_done = False

    def install_icon(self, icon, icon_path):
        """Install icon to the current directory."""
        base_icon = icon["original"]
        ext_orig = icon["orig_ext"]
        theme_icon = icon["theme"]
        ext_theme = icon["theme_ext"]
        icon_size = icon["icon_size"]
        output_icon = icon_path + base_icon
        if ext_theme == ext_orig:
            symlink_file(theme_icon, output_icon)
        elif (ext_theme == "svg" and ext_orig == "png"
              and self.svgtopng.is_svg_enabled):
            if icon_size != self.data.default_icon_size:
                self.svgtopng.to_png(theme_icon, output_icon, icon_size)
            else:
                self.svgtopng.to_png(theme_icon, output_icon)
            mchown(output_icon)
            if "symlinks" in icon.keys():
                for symlink_icon in icon["symlinks"]:
                    symlink_icon = icon_path + symlink_icon
                    symlink_file(output_icon, symlink_icon)
