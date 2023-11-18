import json
import os

from walker import find_config_file


class Configuration:
    """
    Base class for stella'a configuration related tasks.
    """

    def __init__(self) -> None:
        """
        Constructs the `Configuration` class.
        """
        self.config_file = find_config_file()
        if not self.config_file:
            self.config_file = os.path.join(os.path.expanduser("~"), "stella.yml")

        if not os.path.exists(self.config_file):
            self.config = {"browser": "chrome"}
            with open(self.config_file, "w") as f:
                f.write(json.dumps(self.config))

        else:
            with open(self.config_file) as f:
                fc = f.read()
            self.config = json.loads(fc)

    def load_configuration(self) -> dict:
        return self.config

    def set_configuration(self, config: dict):
        with open(self.config_file, "w") as f:
            f.write(json.dumps(config))
