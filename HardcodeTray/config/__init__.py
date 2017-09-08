from HardcodeTray.config.arguments import ArgumentsConfig
from HardcodeTray.config.json import JSONConfig
from HardcodeTray.config.system import SystemConfig

class Config:
    """Store the config from args, json file & system."""

    def __init__(self, args):
        self.data = {}
        self.sources = [
            ArgumentsConfig(args),
            JSONConfig(),
            SystemConfig()
        ]
        self.parse_data()

    def parse_data(self):
        """Parse the data from different sources."""
        for source in self.sources:
            for key, value in source.data.items():
                if value != None or not self.data.get(key):
                    self.data[key] = value

    def get(self, key):
        """Return the value of key."""
        return self.data.get(key)



