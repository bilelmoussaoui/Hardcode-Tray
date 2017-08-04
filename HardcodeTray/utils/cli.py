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
from sys import stdout

def progress(count, count_max, time, app_name=""):
    """Used to draw a progress bar."""
    bar_len = 36
    space = 20
    filled_len = int(round(bar_len * count / float(count_max)))

    percents = round(100.0 * count / float(count_max), 1)
    progress_bar = '#' * filled_len + '.' * (bar_len - filled_len)

    stdout.write("\r{0!s}{1!s}".format(app_name,
                                       " " * (abs(len(app_name) - space))))
    stdout.write('[{0}] {1}/{2} {3}% {4:.2f}s\r'.format(progress_bar,
                                                        count, count_max,
                                                        percents, time))
    print("")
    stdout.flush()
