from os import path, symlink, remove
from shutil import copyfile

from HardcodeTray.log import Logger

class File:
    """

    """

    def __init__(self, file_path):
        """
        :param file_path: the file absolute path
        """
        self.file_path = file_path

    @property
    def extension(self):
        """
        Get the file extension
        :return: str: file extension (png, svg...)
        """
        return path.splitext(self.file_path)[-1].strip(".").lower()

    @property
    def found(self):
        return path.isfile(self.file_path)

    @property
    def content(self):
        with open(self.file_path, 'r') as file_obj:
            data = file_obj.read()
        return data

    def write(self, content):
        with open(self.file_path, 'w') as file_obj:
            file_obj.write(content)

    @property
    def basename(self):
        return path.basename(self.file_path)

    def link(self, link_name):
        """Symlink a file, remove the dest file if already exists."""
        try:
            symlink(self.file_path, link_name)
        except FileExistsError:
            remove(link_name)
            self.link(link_name)
        except FileNotFoundError:
            Logger.warning("File not found: {0}".format(self.file_path))

    def copy(self, dest, overwrite=False):
        if overwrite:
            if dest.found:
                dest.remove()
            copyfile(self.file_path, dest)
        elif not overwrite and not path.isfile(dest):
            copyfile(self.file_path, dest)

    def remove(self):
        if self.found:
            return remove(self.file_path)
        return False
