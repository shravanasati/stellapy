from dataclasses import dataclass
import json
import os


from stellapy.walker import find_config_file


@dataclass(slots=True, frozen=True)
class Script:
    """
    Represents a script in the stella configuration.
    """

    name: str
    url: str
    command: str | list[str]
    shell: bool


@dataclass(slots=True, frozen=True)
class Configuration:
    """
    Represents the stella configuration.
    """

    browser: str
    include_only: list[str]
    scripts: list[Script]
    poll_interval: float  # milliseconds

    @classmethod
    def default(cls):
        return cls(
            browser="firefox",
            include_only=[],
            scripts=[Script("default", "", "echo 'hello'", True)],
            poll_interval=500,
        )

    def to_yaml(self):
        # todo
        return "#lol"

    @classmethod
    def from_yaml(cls):
        # todo
        ...


class ConfigurationManager:
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

    @staticmethod
    def default():
        ...

    def load_configuration(self) -> dict:
        return self.config

    def set_configuration(self, config: dict):
        with open(self.config_file, "w") as f:
            f.write(json.dumps(config))
