#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.6
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
from os import path, remove
from subprocess import PIPE, Popen, call
from modules.svg.svg import SVG
from modules.utils import copy_file, replace_colors


class Inkscape(SVG):
    """Inkscape implemntation of SVG Interface."""

    def __init__(self, colors):
        """Init function."""
        self.colors = colors
        self.cmd = "inkscape"
        self.outfile = "/tmp/hardcode.png"
        if path.exists(self.outfile):
            remove(self.outfile)
        if not self.is_installed():
            raise InkscapeNotInstalled

    def to_png(self, input_file, output_file, width=None, height=None):
        """Convert svg to png."""
        tmp_file = ""
        if len(self.colors) != 0:
            tmp_file = "/tmp/{0!s}".format(path.basename(input_file))
            copy_file(input_file, tmp_file)
            input_file = tmp_file
            replace_colors(input_file, self.colors)
        cmd = [self.cmd, "-z", "-f", input_file, "-e", output_file]
        width, height = self.get_size(width, height)

        if width and height:
            cmd.extend(["-w", str(width), "-h", str(height)])
        p_cmd = Popen(cmd, stdout=PIPE, stderr=PIPE)
        p_cmd.communicate()
        if tmp_file and path.isfile(tmp_file):
            remove(tmp_file)

    def to_bin(self, input_file, width=None, height=None):
        """Convert svg to binary."""
        self.convert_to_png(input_file, self.outfile, width, height)
        with open(self.outfile, 'rb') as temppng:
            binary = temppng.read()
        remove(self.outfile)
        return binary

    def is_installed(self):
        """Check if the tool is installed."""
        ink_flag = call(['which', self.cmd], stdout=PIPE, stderr=PIPE)
        return bool(ink_flag == 0)


class InkscapeNotInstalled(Exception):
    """Exception raised when Inkscape is not installed."""

    def __init__(self):
        """Init Exception."""
        super(InkscapeNotInstalled, self).__init__()
