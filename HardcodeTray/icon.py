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
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk
from HardcodeTray.fs.file import File


class Icon:

    def __init__(self, original_icon, theme_icon, symlinks=[]):
        """
        Create a new Icon Object.
        :param original_icon: the original icon name
        :param theme_icon: the theme icon name
        """
        self.original = File(original_icon)
        self.theme = None
        self.found = False
        self.symlinks = symlinks
        self._verify(theme_icon)

    def _verify(self, theme_icon):
        """
        Verify if the theme_icon exists
        :param theme_icon(str) the theme icon name
        """
        from HardcodeTray.app import App
        app = App.get_default()
        icon_size = app.config.get("icon_size")
        theme = Gtk.IconTheme.get_default()
        self.found = theme.has_icon(theme_icon)
        if self.found:
            icon_info = theme.lookup_icon(theme_icon,
                                          icon_size, 0)
            self.theme = File(icon_info.get_filename())
            self.icon_size = self.get_icon_size(icon_size)

            if self.has_symlinks:
                # Make sure that symlinks have the right extension
                symlinks = []
                for symlink in self.symlinks:
                    if not symlink.extension:
                        symlink += ".{0}".format(self.theme.extension)
                    symlinks.append(symlink)
                self.symlinks = symlinks

    @property
    def has_symlinks(self):
        """Return if the icon has symlinks or not."""
        return self.symlinks != None

    def get_icon_size(self, icon_size):
        """Get the icon size, with hidpi support (depends on the icon name)."""

        # ICON@2x
        icon_name = self.original.split("@")
        if len(icon_name) > 1:
            multiple = int(icon_name[1].split("x")[0])
            if multiple and multiple != 0:
                icon_size *= multiple

        # ICON-22 or ICON_24
        seperators = ["-", "_"]
        for seperator in seperators:
            icon_size = path.splitext(self.original)[0].split(seperator)[-1]
            if icon_size.isdigit():
                icon_size = int(icon_size)
        return icon_size
