#!/usr/bin/python3
from os import path
from platform import machine
from sys import argv

def get_dropbox_version(directory):
    """
        Corrects the hardcoded dropbox directory
        Args:
            directory(str): the default dropbox directory
    """
    version_file = directory.split("{dropbox_version}")[0].split("/")
    del version_file[len(version_file) - 1]
    version_file = "/".join(version_file) + "/VERSION"
    if path.exists(version_file):
        with open(version_file) as f:
            return f.read()
    return ""

dropbox_path = argv[1]
dropbox_path = dropbox_path.replace("{arch}", machine())
dropbox_path = dropbox_path .replace(
    "{dropbox_version}", get_dropbox_version(dropbox_path))
print(dropbox_path)
