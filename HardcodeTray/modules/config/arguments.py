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

from HardcodeTray.utils.icons import replace_to_6hex
from HardcodeTray.modules.log import Logger
from HardcodeTray.modules.theme import Theme


class ArgumentsConfig:
    """Transform arguments to usable things."""

    def __init__(self, args):
        self._args = args

    def icon_size(self):
        """Return Icon size set by args --size."""

        icon_size = self._args.size
        Logger.debug("Arguments/Icon Size: {}".format(icon_size))
        return icon_size

    def theme(self):
        """Return Theme object set by --theme."""
        theme_obj = None

        theme = self._args.theme
        dark_theme = self._args.dark_theme
        light_theme = self._args.light_theme

        if theme:
            theme_obj = Theme(theme)
            Logger.debug("Arguments/Theme: {}".format(theme))
        elif dark_theme and light_theme:
            theme_obj = Theme.new_with_dark_light(dark_theme, light_theme)
            Logger.debug("Arguments/Dark Theme: {}".format(dark_theme))
            Logger.debug("Arguments/Light Theme: {}".format(light_theme))

        return theme_obj

    def conversion_tool(self):
        """Return conversion tool set by --conversion-tool."""
        conversion_tool = self._args.conversion_tool
        Logger.debug("Arguments/Conversion Tool: "
                     "{}".format(conversion_tool))
        return conversion_tool

    def colors(self):
        """Return list of colors set by --change-color."""
        colors = []
        args_colors = self._args.change_color
        if not args_colors:
            args_colors = []
        for color in args_colors:
            color = color.strip().split(" ")
            to_replace = replace_to_6hex(color[0])
            for_replace = replace_to_6hex(color[1])
            if to_replace and for_replace:
                colors.append([to_replace, for_replace])
        return colors

    def only(self):
        """Return list of apps to be fixed."""
        only = self._args.only
        if only:
            only = only.lower().strip()
            Logger.debug("Arguments/Only: {}".format(only))
            return only.split(",")
        return []

    def path(self):
        """Return app path."""
        proposed_path = self._args.path
        if proposed_path:
            if path.isdir(proposed_path):
                return proposed_path
            else:
                raise FileNotFoundError("Please select a valid --path")
        return None

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
