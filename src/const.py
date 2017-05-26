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
from os import getenv, path
from platform import machine

from src.tools import detect_de, get_themes, get_userhome

DB_FOLDER = "./" + path.join("data", "database", "")
USERNAME = getenv("SUDO_USER")
USERHOME = get_userhome(USERNAME)
BACKUP_FOLDER = path.join(USERHOME, ".config", "Hardcode-Tray", "")
CONFIG_FILE = path.join(USERHOME, ".config", "hardcode-tray.json")
KDE_CONFIG_FILE = path.join(USERHOME, ".config",
                            "plasma-org.kde.plasma.desktop-appletsrc")
BACKUP_FILE_FORMAT = "%d-%m-%Y_%H-%M-%S"
LOG_FILE_FORMAT = "%d-%m-%Y_%H-%M-%S"
CHMOD_IGNORE_LIST = ["", "home"]
USER_ID = int(getenv("SUDO_UID"))
GROUP_ID = int(getenv("SUDO_GID"))
ARCH = machine()
THEMES_LIST = get_themes(USERHOME)
DESKTOP_ENV = detect_de()
ICONS_SIZE = [16, 22, 24]
