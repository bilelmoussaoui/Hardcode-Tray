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
from abc import ABCMeta, abstractmethod
from gettext import gettext as _
from importlib import import_module
from os import path, remove
import re
from tempfile import gettempdir, NamedTemporaryFile

from HardcodeTray.enum import ConversionTools
from HardcodeTray.log import Logger
from HardcodeTray.utils.cli import is_installed


class SVG:
    """SVG Interface used by other class's."""

    __metaclass__ = ABCMeta

    def __init__(self, colors):
        """Init function."""
        self.colors = colors
        self.cmd = None

    @staticmethod
    def factory(colors, conversion_tool=None):
        """Create a SVG to PNG object."""
        def load(conversion_tool):
            """Load Objects dynamically."""
            module = ConversionTools.choices()[conversion_tool].lower()
            svg = import_module("HardcodeTray.svg." + module)
            return getattr(svg, conversion_tool)
        svg = None
        if conversion_tool:
            try:
                svg = load(conversion_tool)(colors)
            except SVGNotInstalled:
                exit(_("The selected conversion tool is not installed."))
        else:
            for tool in ConversionTools.choices():
                try:
                    svg = load(tool)(colors)
                    Logger.debug("SVG Factory: Import {}".format(tool))
                    break
                except SVGNotInstalled:
                    Logger.debug("SVG Factory: Failed {}".format(tool))
        if svg:
            return svg
        exit(_("Failed to load any SVG module."))

    def to_png(self, input_file, output_file, width=None, height=None):
        """Convert svg to png and save it in a destination."""
        if width and not height:
            height = width
        elif height and not width:
            width = height

        tmp_file = ""
        if self.colors:
            tmp_file = path.join(gettempdir(), input_file.basename)
            input_file.copy(tmp_file)
            input_file = tmp_file
            SVG.replace_colors(input_file, self.colors)

        self.convert_to_png(input_file, output_file, width, height)
        # Remove uneeded tmp file
        if path.exists(tmp_file):
            remove(tmp_file)

    def to_bin(self, input_file, width=None, height=None):
        """Convert svg to binary."""
        outfile = NamedTemporaryFile().name
        self.to_png(input_file, outfile, width, height)

        with open(outfile, 'rb') as temppng:
            binary = temppng.read()
        remove(outfile)

        return binary

    @staticmethod
    def replace_colors(input_file, colors):
        if input_file.found:
            # Get the file content
            data = input_file.content

            for color in colors:
                data = re.sub(color[0], color[1], data)
            # Write in the new data.
            input_file.write(data)


    @abstractmethod
    def convert_to_png(self, input_file, output_file, width, height):
        """Convert from svg to png. Override the method by childs."""

    def is_installed(self):
        """Check if the tool is installed."""
        return is_installed(self.cmd)

    def __repr__(self):
        return self.__class__.__name__


class SVGNotInstalled(Exception):
    """Exception raised when Inkscape is not installed."""

    def __init__(self):
        """Init Exception."""
        Exception.__init__(self)
