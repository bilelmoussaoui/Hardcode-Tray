from os import path, makedirs

from HardcodeTray.log import Logger


class Directory:
    """

    """

    def __init__(self, dir_path):
        """
        :param dir_path: the directory absolute path
        """
        self.dir_path = dir_path

    @property
    def found(self):
        return path.isdir(self.dir_path)

    def create(self):
        if not self.found:
            Logger.debug("Creating directory: {}".format(self.dir_path))
            makedirs(self.dir_path, exist_ok=True)
