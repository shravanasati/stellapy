import json
import os


class Configuration:
    """
    Base class for stella'a configuration related tasks.
    """
    def __init__(self) -> None:
        """
        Constructs the `Configuration` class.
        """
        config_file = os.path.join(os.path.expanduser("~"), "stella_config.json")

        if not os.path.exists(config_file):
            self.config = {
                "browser": "chrome"
            }
            with open(config_file, 'w') as f:
                f.write(json.dumps(self.config))

        else:
            with open(config_file) as f:
                fc = f.read()
            self.config = json.loads(fc)

    def load_configuration(self) -> dict:
        return self.config