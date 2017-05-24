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
from io import BytesIO

from src.modules.svg.svg import SVG, SVGNotInstalled

try:
    from cairosvg import svg2png
    from cairo import ImageSurface, FORMAT_ARGB32, Context
    from gi import require_version
    require_version('Rsvg', '2.0')
    from gi.repository import Rsvg
    CAIRO_IS_INSTALLED = True
except (ImportError, AttributeError, ValueError):
    CAIRO_IS_INSTALLED = False


class CairoSVG(SVG):
    """Cairo implemntation of SVG Interface."""

    def __init__(self, colors):
        """Init function."""
        super(CairoSVG, self).__init__(colors)

        if not CairoSVG.is_installed():
            raise SVGNotInstalled

    @staticmethod
    def convert_to_png(input_file, output_file, width=None, height=None):
        """Convert svg to png."""
        if width and height:
            handle = Rsvg.Handle()
            svg = handle.new_from_file(input_file)
            dim = svg.get_dimensions()

            img = ImageSurface(
                FORMAT_ARGB32, width, height)
            ctx = Context(img)
            ctx.scale(width / dim.width, height / dim.height)
            svg.render_cairo(ctx)

            png_io = BytesIO()
            img.write_to_png(png_io)
            with open(output_file, 'wb') as fout:
                fout.write(png_io.getvalue())
            fout.close()
            svg.close()
            png_io.close()
            img.finish()
        else:
            with open(input_file, "r") as content_file:
                svg = content_file.read()
            content_file.close()
            fout = open(output_file, "wb")
            svg2png(bytestring=bytes(svg, "UTF-8"), write_to=fout)
            fout.close()

    @staticmethod
    def is_installed():
        """Check if Cairo is installed or not."""
        return CAIRO_IS_INSTALLED
