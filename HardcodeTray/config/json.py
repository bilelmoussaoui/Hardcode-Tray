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
from __future__ import absolute_import

from json import load
from os import path

from HardcodeTray.const import CONFIG_FILE, ICONS_SIZE
from HardcodeTray.log import Logger
from HardcodeTray.theme import Theme


class JSONConfig:
    """Read JSON config file and make it usable."""

    def __init__(self):
        self._config = {}
        self.data = {}
        self.read_file()
        self.parse_data()

    def read_file(self):
        """Read the config file."""
        if path.isfile(CONFIG_FILE):
            Logger.debug("Reading config file: {}".format(CONFIG_FILE))
            with open(CONFIG_FILE, 'r') as data:
                try:
                    self._config = load(data)
                except ValueError:
                    Logger.warning("The config file is "
                                   "not a valid json file.")
        else:
            Logger.debug("Config file: Not found.")

    def parse_data(self):
        """Parse the config file data and store it."""
        self.data["icon_size"] = self.icon_size
        self.data["blacklist"] = self.blacklist
        self.data["theme"] = self.theme
        self.data["conversion_tool"] = self.conversion_tool
        self.data["nwjs"] = self.nwjs
        self.data["scaling_factor"] = self.scaling_factor
        self.data["backup_ignore"] = self.backup_ignore

    @property
    def icon_size(self):
        """Return the icon size in the config file."""
        icon_size = self._config.get("icon_size")
        Logger.debug("Config/Icon Size: {}".format(icon_size))
        if icon_size not in ICONS_SIZE:
            Logger.warning("Config/Icon Size: Incorrect.")
            Logger.debug("Config/Icon Size: Detected icon "
                         "size will be used.")
        return icon_size

    @property
    def theme(self):
        """Return theme object set in the config file."""
        theme = self._config.get("theme")
        if theme:
            theme_obj = Theme(theme)
            Logger.debug("Config/Theme: {}".format(theme))
            return theme_obj
        return None

    @property
    def conversion_tool(self):
        """Return conversion tool set in the config file."""
        conversion_tool = self._config.get("conversion_tool")
        Logger.debug("Config/Conversion Tool: {}".format(conversion_tool))
        return conversion_tool

    @property
    def blacklist(self):
        """Return a list of blacklist apps."""
        blacklist = self._config.get("blacklist", [])
        Logger.debug("Config/Blacklist: "
                     "{}".format(",".join(blacklist)))
        return blacklist

    @property
    def nwjs(self):
        """Return nwjs sdk path."""
        nwjs = self._config.get("nwjs")
        if nwjs and path.exists(nwjs):
            Logger.debug("Config/NWJS SDK: {}".format(nwjs))
            return nwjs
        return None

    @property
    def scaling_factor(self):
        """Return widget scaling factor."""
        scaling_factor = self._config.get("scaling_factor")
        if scaling_factor and scaling_factor > 1:
            return scaling_factor
        return 1

    @property
    def backup_ignore(self):
        """Return a boolean, ignore backup or not."""
        backup_ignore = self._config.get("backup_ignore")
        Logger.debug("Config/Backup Ignore: {}".format(str(backup_ignore)))
        return backup_ignore
