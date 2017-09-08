

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
        pass
