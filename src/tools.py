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
from os import environ, listdir, path
from subprocess import check_output

from src.modules.log import Logger


DE = ["i3", "cinnamon", "budgie", "deepin", "pantheon",
      "gnome", "kde", "unity", "mate", "xfce"]



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
        desktop_env = [environ.get("DESKTOP_SESSION").lower(),
                       environ.get("XDG_CURRENT_DESKTOP").lower()]
    except AttributeError:
        desktop_env = []

    for desktop in DE:
        if desktop in desktop_env:
            Logger.debug("DE: {0}".format(desktop.title()))
            return desktop
    Logger.debug("DE not detected.")
    return "other"


def get_themes(userhome):
    """Return a list of installed icon themes."""
    paths = ["/usr/share/icons/",
             "{0}/.local/share/icons/".format(userhome),
             "{0}/.icons/".format(userhome)]
    themes = []
    for icon_path in paths:
        try:
            sub_dirs = listdir(icon_path)
            for theme in sub_dirs:
                theme_path = path.join(icon_path, theme, "")
                theme_index = "{0!s}index.theme".format(theme_path)
                if path.exists(theme_index) and theme not in themes:
                    themes.append(theme)
        except FileNotFoundError:
            pass
    return themes
