from HardcodeTray.parser.database import Database


class QtDatabase(Database):
    def __init__(self, *args, **kwargs):
        Database.__init__(self, *args, **kwargs)
        self.force_create_folder = True
        self.backup_ignore = True
