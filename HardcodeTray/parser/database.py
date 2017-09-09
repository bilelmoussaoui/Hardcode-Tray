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
from importlib import import_module
from HardcodeTray.enum import ApplicationType


class Database:

    def __init__(self, *args, **kwargs):
        self.db_file = None
        self.name = None
        self.app_paths = []
        self.icons_paths = []
        self.icons = []
        self.module = None
        self.binary = None
        self.symlinks = []
        self.force_create_folder = False
        self.backup_ignore = False
        self.is_installed = False
        for key, value in kwargs.items():
            setattr(self, key, value)

    def factory(self):
        """Create an instance of Application."""
        """Application factory, return an instance of Application."""
        def load(module_name):
            """Load Objects dynamically."""
            module, class_name = None, None
            for key, value in ApplicationType.choices().items():
                if key == module_name:
                    module = key
                    class_name = value
                    break
            module_ = import_module("HardcodeTray.applications." + module)
            if hasattr(module_, class_name):
                return getattr(module_, class_name)
            return None
        object_ = load(self.module)
        if object_:
            return object(self)
        return None
