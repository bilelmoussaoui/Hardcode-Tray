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
from os import listdir, path
from subprocess import Popen, call, PIPE

from HardcodeTray.modules.log import Logger

def execute(command_list, verbose=True, shell=False, working_directory=None):
    """
    Run a command using "Popen".

    Args :
        command_list(list)
        verbose(bool)
    """
    Logger.debug("Executing command: {0}".format(" ".join(command_list)))
    if working_directory:
        cmd = Popen(command_list, stdout=PIPE, stderr=PIPE, shell=shell,
                    cwd=working_directory)
    else:
        cmd = Popen(command_list, stdout=PIPE, stderr=PIPE, shell=shell)

    output, error = cmd.communicate()
    if verbose and error:
        Logger.error(error.decode("utf-8").strip())
    return output


def is_installed(binary):
    """Check if a binary file exists/installed."""
    ink_flag = call(['which', binary], stdout=PIPE, stderr=PIPE)
    return bool(ink_flag == 0)

def get_exact_folder(key, directory, condition):
    """
        Get subdirs and apply a condition on each until one is found.
    """
    dirs = directory.split(key)
    exact_directory = ""

    if path.isdir(dirs[0]):
        directories = listdir(dirs[0])
        for dir_ in directories:
            if condition(path.join(dirs[0], dir_, "")):
                exact_directory = dir_
                break

    if exact_directory:
        directory = directory.replace(key, exact_directory)

    return directory
