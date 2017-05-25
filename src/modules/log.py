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
import logging
from os import makedirs, path
from time import strftime


class Logger:
    """
    Logger class, logs error and other messages on /tmp/Hardcode-Tray.
    """
    FORMAT = "[%(levelname)-s] %(asctime)s %(message)s"
    DATE = "%Y-%m-%d %H:%M:%S"
    PATH = "/tmp/Hardcode-Tray/"
    _log = None

    @staticmethod
    def get_default():
        """Return default instance of Logger."""
        if Logger._log is None:
            from src.const import LOG_FILE_FORMAT
            logger = logging.getLogger('hardcode-tray')

            log_file = "{0}.log".format(strftime(LOG_FILE_FORMAT))
            tmp_file = path.join(Logger.PATH, log_file)

            if not path.exists(path.dirname(tmp_file)):
                makedirs(path.dirname(tmp_file))

            if not path.exists(tmp_file):
                with open(tmp_file, 'w') as tmp_obj:
                    tmp_obj.write('')

            handler = logging.FileHandler(tmp_file)
            formater = logging.Formatter(Logger.FORMAT, Logger.DATE)
            handler.setFormatter(formater)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)

            Logger._log = logging.getLogger("hardcode-tray")
        return Logger._log

    @staticmethod
    def warning(msg):
        """Log warning message."""
        Logger.get_default().warning(msg)

    @staticmethod
    def debug(msg):
        """Log debug message."""
        Logger.get_default().debug(msg)

    @staticmethod
    def info(msg):
        """Log info message."""
        Logger.get_default().info(msg)

    @staticmethod
    def error(msg):
        """Log error message."""
        Logger.get_default().error(msg)
