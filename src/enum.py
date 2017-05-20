#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.7
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

from .modules.svg.inkscape import Inkscape
from .modules.svg.svgcairo import CairoSVG
from .modules.svg.rsvgconvert import RSVGConvert
from .modules.svg.imagemagick import ImageMagick
from .modules.svg.svgexport import SVGExport

class Action:
    APPLY = 1
    REVERT = 2
    CLEAR_CACHE = 3

CONVERSION_TOOLS = {"Inkscape": Inkscape,
                    "CairoSVG": CairoSVG,
                    "RSVGConvert": RSVGConvert,
                    "ImageMagick": ImageMagick,
                    "SVGExport": SVGExport
                   }
