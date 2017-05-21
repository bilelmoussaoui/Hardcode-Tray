from os import path
from src.const import ARCH, USERHOME, PATH_SCRIPTS_FOLDER
from src.utils import create_dir, execute

class Path:
    DB_VARIABLES = {
        "{userhome}" : USERHOME,
        "{size}" : 22, # Fix me
        "{arch}" : ARCH
    }
    def __init__(self, absolute_path, exec_path_script=None):
        self._path = absolute_path
        self._path_script = exec_path_script
        self._found = True
        self._validate()

    def append(self, filename):
        return path.join(self.path, filename)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def found(self):
        return self._found

    def _validate(self):
        for key, value in Path.DB_VARIABLES.items():
            self.path = self.path.replace(key, str(value))
        if self._path_script:
            # If application does need a specific script to get the right path
            script_path = path.join(PATH_SCRIPTS_FOLDER, self._path_script)
            if path.exists(script_path):
                self.path = execute([script_path, self.path],
                                    verbose=True).decode("utf-8").strip()
            else:
                logging.error("Script file `%s` not found", script_path)
        if not path.exists(self.path):
            self._found = False
