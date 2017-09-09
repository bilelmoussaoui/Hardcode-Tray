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
from shutil import rmtree

from HardcodeTray.decorators import revert_wrapper, symlinks_installer
from HardcodeTray.log import Logger
from HardcodeTray.applications import Application


class QtApplication(Application):
    """Qt application, works only with the patched version of sni-qt."""
    BACKUP_IGNORE = True

    def __init__(self, parser):
        """Init method."""
        Application.__init__(self, parser)

    @symlinks_installer
    def install_icon(self, icon, icon_path):
        """Install icon to the current directory."""
        icon.original = "{}.{}".format(icon.original,
                                       icon.theme_ext)

        base_icon = icon.original
        theme_icon = icon.theme
        output_icon = path.join(str(icon_path), base_icon)
        symlink_file(theme_icon, output_icon)

    @revert_wrapper
    def reinstall(self):
        """Overwrite the reinstall function, and remove the whole dir."""
        done = False
        for icon_path in self.icons_path:
            icon_path = str(icon_path)
            if path.isdir(icon_path):
                rmtree(icon_path)
                Logger.debug("Qt Application: Reverting"
                             " {} is done.".format(self.name))
                done = True
        if not done:
            Logger.debug("Qt Application: Reverting "
                         "{} is not done.".format(self.name))
        self.success = done
