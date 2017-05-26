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
from os import listdir, path, remove
from shutil import move
from time import strftime

from src.const import BACKUP_FILE_FORMAT, BACKUP_FOLDER
from src.modules.log import Logger
from src.utils import copy_file, create_dir, mchown


class Backup:
    """
        Handle backup/revert for each app.
    """

    def __init__(self, application):
        self._app = application
        self._backup_dir = None
        self._exists = False
        self._selected_backup = None

    @property
    def exists(self):
        """Return if the backup does exists or not."""
        return self._exists

    @property
    def app(self):
        """Return the instance of Application object."""
        return self._app

    @property
    def backup_dir(self):
        """Return the backup directory of the current application."""
        return self._backup_dir

    @backup_dir.setter
    def backup_dir(self, backup_dir):
        self._backup_dir = backup_dir

    @property
    def selected_backup(self):
        """Return the selected backup directory during the revert process."""
        return self._selected_backup

    @selected_backup.setter
    def selected_backup(self, selected_backup):
        self._selected_backup = selected_backup

    def create_backup_dir(self):
        """Create a backup directory for an application (application_name)."""
        backup_dir = path.join(BACKUP_FOLDER,
                               self.app.name,
                               strftime(BACKUP_FILE_FORMAT), "")
        exists = True
        new_backup_dir = backup_dir
        i = 1

        while exists:
            if path.exists(new_backup_dir):
                new_backup_dir = backup_dir + "_" + str(i)
            if not path.isdir(new_backup_dir):
                Logger.debug("Create new backup folder "
                             "for {}".format(self.app.name))
                create_dir(new_backup_dir)
                exists = False
            i += 1

        self._backup_dir = new_backup_dir

    def create(self, filename):
        """Backup functions."""
        from src.app import App

        if not App.get("backup_ignore"):
            if not self.backup_dir:
                self.create_backup_dir()

            backup_file = path.join(self.backup_dir,
                                    path.basename(filename))

            if path.exists(filename):
                Logger.debug("Backup file: {0} to: {1}".format(filename,
                                                               backup_file))
                copy_file(filename, backup_file, True)
                mchown(backup_file)

    def file(self, filename, binary):
        """Backup a binary content as a file."""
        tempfile = "/" + path.join("tmp", path.basename(filename))

        with open(tempfile, 'wb') as fobj:
            fobj.write(binary)

        self.create(tempfile)
        remove(tempfile)

    def get_backup_file(self, filename):
        """Return the backup file path."""
        try:
            backup_file = path.join(BACKUP_FOLDER,
                                    self.app.name,
                                    self.selected_backup,
                                    filename)

            if path.exists(backup_file):
                return backup_file
        except (ValueError, TypeError):
            pass
        return None

    def get_backup_folders(self):
        """Get a list of backup folders of a sepecific application."""
        try:
            return listdir(path.join(BACKUP_FOLDER, self.app.name))
        except FileNotFoundError:
            return []

    def _display_choices(self, restore_points):
        """Display a list of possible restore points."""
        i = 1
        for backup_folder in restore_points:
            print("{}) {}/{} ".format(str(i),
                                      self.app.name,
                                      backup_folder))
            i += 1

    def select(self):
        """Show a select option for the backup of each application."""
        backup_folders = self.get_backup_folders()
        total = len(backup_folders)

        if total != 0:
            backup_folders.sort()

            self._display_choices(backup_folders)
            print("(Q)uit to cancel")

            has_chosen = False
            stopped = False

            while not has_chosen and not stopped:
                try:
                    selected = input("Select a restore date : ")
                    if selected in ["q", "quit", "exit"]:
                        stopped = True
                    selected = int(selected)
                    if 1 <= selected <= total:
                        has_chosen = True
                        self._exists = True
                        self._selected_backup = backup_folders[selected - 1]
                except ValueError:
                    pass
                except KeyboardInterrupt:
                    exit()

            if stopped:
                Logger.debug("The user stopped the "
                             "reversion for {}".format(self.app.name))
            else:
                Logger.debug("No backup folder found for "
                             "the application {0}".format(self.app.name))

    def remove(self, file_name):
        """
        Backup functions, enables reverting.

        Args:
            icon(str) : the original icon name
            revert(bool) : True: revert, False: only backup
        """
        try:
            backup_file = path.join(BACKUP_FOLDER,
                                    self.app.name,
                                    self.selected_backup,
                                    path.basename(file_name))

            if path.isfile(backup_file):
                move(backup_file, file_name)
        except (TypeError, ValueError):
            self._exists = False
