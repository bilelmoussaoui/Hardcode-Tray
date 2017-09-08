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
import re

from HardcodeTray.log import Logger
from HardcodeTray.theme import Theme


class ArgumentsConfig:
    """Transform arguments to usable things."""

    def __init__(self, args):
        self.data = {}
        self._args = args
        self.parse_data()

    def parse_data(self):
        """Parse the argument data and store it in a dict."""
        self.data["icon_size"] = self.icon_size
        self.data["theme"] = self.theme
        self.data["conversion_tool"] = self.conversion_tool
        self.data["colors"] = self.colors
        self.data["only"] = self.only
        self.data["action"] = self.action

    @property
    def icon_size(self):
        """Return Icon size set by args --size."""

        icon_size = self._args.size
        Logger.debug("Arguments/Icon Size: {}".format(icon_size))
        return icon_size

    @property
    def theme(self):
        """Return Theme object set by --theme."""
        theme = self._args.theme
        if theme:
            theme_obj = Theme(theme)
            Logger.debug("Arguments/Theme: {}".format(theme))
            return theme_obj
        return None

    @property
    def conversion_tool(self):
        """Return conversion tool set by --conversion-tool."""
        conversion_tool = self._args.conversion_tool
        Logger.debug("Arguments/Conversion Tool: "
                     "{}".format(conversion_tool))
        return conversion_tool

    @property
    def colors(self):
        """Return list of colors set by --change-color."""
        colors = []

        def validate_color(color):
            """Validate and replace 3hex colors to 6hex ones."""
            if re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color):
                if len(color) == 4:
                    color = "#{0}{0}{1}{1}{2}{2}".format(color[1],
                                                         color[2],
                                                         color[3])
                return color
            else:
                exit(_("Invalid color {}").format(color))

        args_colors = self._args.change_color
        if not args_colors:
            args_colors = []
        for color in args_colors:
            color = color.strip().split(" ")
            to_replace = validate_color(color[0])
            for_replace = validate_color(color[1])
            colors.append([to_replace, for_replace])
        return colors

    @property
    def only(self):
        """Return list of apps to be fixed."""
        only = self._args.only
        if only:
            only = only.lower().strip()
            Logger.debug("Arguments/Only: {}".format(only))
            return only.split(",")
        return []

    @property
    def action(self):
        """Return which action to be done."""
        from HardcodeTray.enum import Action
        action = None
        is_apply = self._args.apply
        is_revert = self._args.revert
        is_clear_cache = self._args.clear_cache

        if is_apply and is_revert:
            raise ValueError
        # Can't apply/revert and clear cache on the same time
        elif (is_apply or is_revert) and is_clear_cache:
            raise ValueError
        elif is_apply:
            action = Action.APPLY
        elif is_revert:
            action = Action.REVERT
        elif is_clear_cache:
            action = Action.CLEAR_CACHE
        return action
