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
from os import environ, path
from subprocess import check_output

from src.modules.log import Logger


def get_userhome(username):
    """Get real user home path."""
    userhome = check_output('sh -c "echo $HOME"', shell=True,
                            universal_newlines=True).strip()
    if userhome.lower() == "/root":
        userhome = path.join("home", username)
    userhome = path.join(path.sep, userhome)
    return userhome


def detect_de():
    """Detect the desktop environment, used to choose the proper icons size."""
    try:
        desktop_env = [environ.get("DESKTOP_SESSION").lower(
        ), environ.get("XDG_CURRENT_DESKTOP").lower()]
    except AttributeError:
        desktop_env = []
    known_desktop = ["pantheon", "gnome", "kde", "unity", "mate", "xfce"]
    for desktop in known_desktop:
        if desktop in desktop_env:
            Logger.debug(
                "Desktop environnement detected : {0}".format(desktop.title()))
            return desktop
    Logger.debug("The desktop environment couldn't be detected")
    return "other"
