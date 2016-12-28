#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.6
Website : https://github.com/bil-elmoussaoui/Hardcode-Tray
Licence : The script is released under GPL, uses a modified script
     form Chromium project released under BSD license
This file is part of Hardcode-Tray.
Hardcode-Tray is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
TwoFactorAuth is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Hardcode-Tray. If not, see <http://www.gnu.org/licenses/>.
"""
from modules.utils import backup, revert, symlink_file, mchown


class Application:
    """Application class."""

    STEP = 0
    supported_icons_cnt = 0

    def __init__(self, application_data, svgtopng):
        """
        Init method.

        @json_file(str): the json database file name
        @custom_path(str): used when the application is compiled
                    and installed in an other customn path
        """
        self.svgtopng = svgtopng
        self.app = application_data
        self.supported_icons_cnt = len(self.get_icons())

    def get_name(self):
        """Return the application name."""
        return self.app.data["name"]

    def get_icons(self):
        """Return the application icons."""
        return self.app.data["icons"]

    def get_app_paths(self):
        """Return the application installation paths."""
        return self.app.data["app_path"]

    def get_icons_path(self):
        """Return the application installation paths."""
        return self.app.data["icons_path"]

    def get_symlinks(self):
        """Return application symlinks."""
        return self.app.data["symlinks"]

    def has_symlinks(self):
        """Return a boolean value if either the application have symlinks."""
        return "symlinks" in self.app.data.keys()

    def install_symlinks(self):
        """Create symlinks for some applications files."""
        if self.has_symlinks():
            symlinks = self.get_symlinks()
            for syml in symlinks:
                for d in self.get_app_paths():
                    root = symlinks[syml]["root"]
                    dest = d + symlinks[syml]["dest"]
                    backup(dest)
                    symlink_file(root, dest)

    def remove_symlinks(self):
        """Remove symlinks created by the application."""
        if self.has_symlinks():
            symlinks = self.get_symlinks()
            for syml in symlinks:
                for d in self.get_app_paths():
                    revert(d + symlinks[syml]["dest"])

    def install(self):
        """Install the application icons."""
        self.install_symlinks()
        for icon in self.get_icons():
            base_icon = icon["original"]
            for icon_path in self.get_icons_path():
                output_icon = icon_path + base_icon
                if not self.app.data["backup_ignore"]:
                    backup(output_icon)
                self.install_icon(icon, icon_path)

    def reinstall(self):
        """Reinstall the application icons and remove symlinks."""
        self.remove_symlinks()
        for icon in self.get_icons():
            base_icon = icon["original"]
            for icon_path in self.get_icons_path():
                output_icon = icon_path + base_icon
                if not self.app.data["backup_ignore"]:
                    revert(output_icon)

    def install_icon(self, icon, icon_path):
        """Install icon to the current directory."""
        base_icon = icon["original"]
        ext_orig = icon["orig_ext"]
        fname = icon["theme"]
        ext_theme = icon["theme_ext"]
        icon_size = icon["icon_size"]
        output_icon = icon_path + base_icon
        if ext_theme == ext_orig:
            symlink_file(fname, output_icon)
        elif ext_theme == "svg" and ext_orig == "png":
            if self.svgtopng.is_svg_enabled():
                try:  # Convert the svg file to a png one
                    if icon_size != self.app.default_icon_size:
                        self.svgtopng.to_png(fname, output_icon, icon_size)
                    else:
                        self.svgtopng.to_png(fname, output_icon)
                    mchown(output_icon)
                    if "symlinks" in icon.keys():
                        for symlink_icon in icon["symlinks"]:
                            symlink_icon = icon_path + symlink_icon
                            symlink_file(output_icon, symlink_icon)
                # TODO: remove to general exception catch
                except Exception as e:
                    print(e)
