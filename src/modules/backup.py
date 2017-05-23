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
from os import path, listdir, remove
from shutil import move
from time import strftime
from src.const import BACKUP_EXTENSION, BACKUP_FILE_FORMAT, BACKUP_FOLDER
from src.utils import create_dir, copy_file, mchown
from src.modules.log import Logger


class Backup:
    """
        Handle backup/revert for each app.
    """
    def __init__(self, application):
        self._app = application
        self._backup_dir = None
        self._selected_backup = None

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
        current_time_folder = strftime(BACKUP_FILE_FORMAT)
        back_dir = path.join(BACKUP_FOLDER, self.app.name,
                             current_time_folder, "")
        exists = True
        new_back_dir = back_dir
        i = 1
        while exists:
            if path.exists(new_back_dir):
                new_back_dir = back_dir + "_" + str(i)
            if not path.isdir(new_back_dir):
                create_dir(new_back_dir)
                exists = False
            i += 1
        self._backup_dir = new_back_dir

    def create(self, file_name):
        """Backup functions."""
        from src.app import App
        if not App.config().get("backup-ignore", False):
            if not self.backup_dir:
                print("hey")
                self.create_backup_dir()
            back_file = path.join(self.backup_dir, path.basename(
                file_name) + BACKUP_EXTENSION)
            if path.exists(file_name):
                Logger.debug("Backup current file {0} to{1}".format(
                    file_name, back_file))
                copy_file(file_name, back_file, True)
                mchown(back_file)

    def file(self, filename, binary):
        """Backup a binary content as a file."""
        tempfile = "/" + path.join("tmp", path.basename(filename))
        with open(tempfile, 'wb') as fobj:
            fobj.write(binary)
        self.create(tempfile)
        remove(tempfile)

    def get_backup_file(self, filename):
        """Return the backup file path."""
        backup_folder = path.join(BACKUP_FOLDER, self.app.name, self.selected_backup)
        backup_file = path.join(backup_folder, filename + BACKUP_EXTENSION)
        if path.exists(backup_file):
            return backup_file
        return None

    def get_backup_folders(self):
        """Get a list of backup folders of a sepecific application."""
        return listdir(path.join(BACKUP_FOLDER, self.app.name))

    def select(self):
        """Show a select option for the backup of each application."""
        backup_folders = self.get_backup_folders()
        max_i = len(backup_folders)
        if max_i != 0:
            backup_folders.sort()
            i = 1
            for backup_folder in backup_folders:
                print("{0}) {1}/{2} ".format(str(i),
                                             self.app.name, backup_folder))
                i += 1
            print("(Q)uit to not revert to any version")
            have_chosen = False
            stopped = False
            while not have_chosen and not stopped:
                try:
                    selected_backup = input(
                        "Select a restore date : ").strip().lower()
                    if selected_backup in ["q", "quit", "exit"]:
                        stopped = True
                    selected_backup = int(selected_backup)
                    if 1 <= selected_backup <= max_i:
                        have_chosen = True
                        self._selected_backup = backup_folders[selected_backup - 1]
                except ValueError:
                    pass
                except KeyboardInterrupt:
                    exit()
            if stopped:
                Logger.debug("The user stopped the reversion for {0}".format(
                    self.app.name))
            else:
                Logger.debug("No backup folder found "
                             "for the application {0}".format(
                                 self.app.name))

    def remove(self, file_name):
        """
        Backup functions, enables reverting.

        Args:
            icon(str) : the original icon name
            revert(bool) : True: revert, False: only backup
        """
        back_dir = path.join(BACKUP_FOLDER, self.app.name, self.selected_backup, "")
        if path.exists(back_dir):
            back_file = path.join(back_dir, path.basename(file_name) + BACKUP_EXTENSION)
            if path.isfile(back_file):
                move(back_file, file_name)
