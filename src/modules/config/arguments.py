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

from src.utils import replace_to_6hex
from src.modules.log import Logger
from src.modules.theme import Theme


class ArgumentsConfig:
    """Transform arguments to usable things."""
    _args = None
    _icon_size = None
    _colors = None
    _path = None
    _only = None
    _conversion_tool = None
    _theme = None
    _action = None

    @staticmethod
    def set_args(args):
        """Set args."""
        ArgumentsConfig._args = args

    @staticmethod
    def args():
        """Return list of args."""
        return ArgumentsConfig._args

    @staticmethod
    def icon_size():
        """Return Icon size set by args --size."""
        if ArgumentsConfig._icon_size is None:
            icon_size = ArgumentsConfig.args().size
            Logger.debug("Arguments/Icon Size: {}".format(icon_size))
            ArgumentsConfig._icon_size = icon_size
        return ArgumentsConfig._icon_size

    @staticmethod
    def theme():
        """Return Theme object set by --theme."""
        if not ArgumentsConfig._theme:
            theme = ArgumentsConfig.args().theme
            dark_theme = ArgumentsConfig.args().dark_theme
            light_theme = ArgumentsConfig.args().light_theme
            if theme:
                ArgumentsConfig._theme = Theme(theme)
                Logger.debug("Arguments/Theme: {}".format(theme))
            elif dark_theme and light_theme:
                ArgumentsConfig._theme = {
                    "dark": Theme(dark_theme),
                    "light": Theme(light_theme)
                }
                Logger.debug("Arguments/Dark Theme: {}".format(dark_theme))
                Logger.debug("Arguments/Light Theme: {}".format(light_theme))
        return ArgumentsConfig._theme

    @staticmethod
    def conversion_tool():
        """Return conversion tool set by --conversion-tool."""
        if not ArgumentsConfig._conversion_tool:
            conversion_tool = ArgumentsConfig.args().conversion_tool
            Logger.debug(
                "Arguments/Conversion Tool: {}".format(conversion_tool))
            ArgumentsConfig._conversion_tool = conversion_tool
        return ArgumentsConfig._conversion_tool

    @staticmethod
    def colors():
        """Return list of colors set by --change-color."""
        if not ArgumentsConfig._colors:
            colors = []
            args_colors = ArgumentsConfig.args().change_color
            if not args_colors:
                args_colors = []
            for color in args_colors:
                color = color.strip().split(" ")
                to_replace = replace_to_6hex(color[0])
                for_replace = replace_to_6hex(color[1])
                colors.append([to_replace, for_replace])
            ArgumentsConfig._colors = colors
        return ArgumentsConfig._colors

    @staticmethod
    def only():
        """Return list of apps to be fixed."""
        if ArgumentsConfig._only is None:
            only = ArgumentsConfig.args().only
            if only:
                only = only.lower().strip()
                Logger.debug("Arguments/Only: {}".format(only))
                ArgumentsConfig._only = only.split(",")
        return ArgumentsConfig._only

    @staticmethod
    def path():
        """Return app path."""
        if ArgumentsConfig._path is None:
            proposed_path = ArgumentsConfig.args().path
            if proposed_path:
                if path.isdir(proposed_path):
                    ArgumentsConfig._path = proposed_path
                else:
                    raise FileNotFoundError("Please select a valid --path")
        return ArgumentsConfig._path

    @staticmethod
    def action():
        """Return which action to be done."""
        if ArgumentsConfig._action is None:
            from src.enum import Action
            action = None
            is_apply = ArgumentsConfig.args().apply
            is_revert = ArgumentsConfig.args().revert
            is_clear_cache = ArgumentsConfig.args().clear_cache

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
            ArgumentsConfig._action = action
        return ArgumentsConfig._action
