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


class Action:
    """
        Different possible actions
    """
    APPLY = {"str": "Apply", "id": 1}
    REVERT = {"str": "Revert", "id": 2}
    CLEAR_CACHE = {"str": "Clear Cache", "id": 3}

    @staticmethod
    def choices(use_str=False):
        """Return a dict of different choices."""
        choices = {}
        for choice in Action.__dict__:
            if hasattr(Action, choice):
                try:
                    value = getattr(Action, choice)
                    if isinstance(value, dict):
                        if use_str:
                            choices[value["str"]] = choice
                        else:
                            choices[value["id"]] = choice
                except (TypeError, ValueError):
                    pass
        return choices

    @staticmethod
    def get_by_id(id_):
        for choice in Action.__dict__:
            if hasattr(Action, choice):
                value = getattr(Action, choice)
                if isinstance(value, dict) and value["id"] == id_:
                    return value
        return None

class ConversionTools:
    """
        Supported Conversion tools
    """
    INKSCAPE = "Inkscape"
    CAIROSVG = "CairoSVG"
    RSVGCONVERT = "RSVGConvert"
    SVGEXPROT = "SVGExport"
    IMAGEMAGICK = "ImageMagick"

    @staticmethod
    def choices():
        """Return a dict of different choices."""
        choices = {}
        for choice in ConversionTools.__dict__:
            if hasattr(ConversionTools, choice):
                value = getattr(ConversionTools, choice)
                if isinstance(value, str) and choice not in ["__module__", "__doc__"]:
                    choices[value] = choice
        return choices


class ApplicationType:
    """
        Different Applications Type
    """
    ELECTRON = "ElectronApplication"
    ZIP = "ZipApplication"
    PAK = "PakApplication"
    NWJS = "NWJSApplication"
    QT = "QtApplication"
    NORMAL = "Application"

    @staticmethod
    def choices():
        """Return a dict of different choices."""
        choices = {}
        for choice in ApplicationType.__dict__:
            if hasattr(ApplicationType, choice):
                value = getattr(ApplicationType, choice)
                if isinstance(value, str) and choice != "__module__":
                    choices[choice.lower()] = value
        return choices
