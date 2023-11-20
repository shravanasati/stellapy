import os
from dataclasses import asdict, dataclass
from io import StringIO
from logging import exception

from ruamel.yaml import YAML

from stellapy.logger import log
from stellapy.walker import find_config_file

# todo alter the schema URL
YAML_SCHEMA_TEXT = "# yaml-language-server: $schema=./schema.json\n"


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
        yaml = YAML()
        s = StringIO()
        yaml.dump(data=asdict(self), stream=s)
        s.seek(0)
        content = YAML_SCHEMA_TEXT + s.read()
        s.close()
        return content

    @classmethod
    def from_yaml(cls, s: str):
        yaml = YAML()
        data = yaml.load(s)
        # load all scripts as Script (instead of a dictionary) in data
        scripts = [Script(**script) for script in data.get("scripts", [])]
        data["scripts"] = scripts
        return cls(**data)


# todo handle incorrect configuration


class ConfigurationManager:
    """
    Base class for stella'a configuration related tasks.
    """

    def __init__(self, config_file: str | None = None) -> None:
        """
        Constructs the `Configuration` class.
        """
        try:
            self.config_file = ""

            # if a config file is given use it
            if config_file:
                if os.path.exists(config_file):
                    self.config_file = config_file
            else:
                self.config_file = find_config_file()

            if not self.config_file:
                self.config_file = os.path.join(os.path.expanduser("~"), "stella.yml")

            if not os.path.exists(self.config_file):
                self.config = Configuration.default()
                with open(self.config_file, "w") as f:
                    f.write(self.config.to_yaml())

            else:
                with open(self.config_file) as f:
                    fc = f.read()
                self.config = Configuration.from_yaml(fc)

        except Exception as e:
            log("error", "unable to load configuration!")
            exception(e)

    def load_configuration(self) -> Configuration:
        return self.config


if __name__ == "__main__":
    print(Configuration.from_yaml(Configuration.default().to_yaml()))
