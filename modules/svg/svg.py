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
TwoFactorAuth is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Hardcode-Tray. If not, see <http://www.gnu.org/licenses/>.
"""


class SVG:
    """SVG Interface used by other class's."""
    is_svg_enabled = True

    def convert_to_png(self, input_file, output_file, width=None, height=None):
        """Convert svg to png and save it in a destination."""
        pass

    def convert_to_bin(self, input_file, width=None, height=None):
        """Convert svg to binary."""
        pass

    def is_installed(self):
        """Check if the tool is installed."""
        pass

    def  is_svg_enabled(self):
        """Return if the svg to png conversion tools are activated."""
        return self.is_svg_enabled

    def set_is_svg_enabled(self, is_svg_enabled):
        """Disable using svg to png conversion tools."""
        self.is_svg_enabled = is_svg_enabled
