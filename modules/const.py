#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.6.5
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
from subprocess import check_output

DB_FOLDER = path.join("database", "")
CONVERSION_TOOLS = ["Inkscape", "CairoSVG",
                    "RSVGConvert", "ImageMagick", "SVGExport"]
BACKUP_EXTENSION = ".bak"
USERNAME = getenv("SUDO_USER")
USERHOME = check_output('sh -c "echo $HOME"', shell=True,
                        universal_newlines=True).strip()
if USERHOME.lower() == "/root":
    USERHOME = path.join("", "home", getenv("SUDO_USER"))
BACKUP_FOLDER = path.join(USERHOME, ".config", "Hardcode-Tray", "")
BACKUP_FILE_FORMAT = "%d-%m-%Y_%H-%M-%S"
CHMOD_IGNORE_LIST = ["", "home"]
USER_ID = int(getenv("SUDO_UID"))
GROUP_ID = int(getenv("SUDO_GID"))
ARCH = machine()
FIXED_APPS = []
REVERTED_APPS = []
