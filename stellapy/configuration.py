import json
import os
from dataclasses import asdict, dataclass
from io import StringIO
from logging import exception
from typing import Any

import importlib.resources
from jsonschema import Draft6Validator, ValidationError, validate
from ruamel.yaml import YAML

from stellapy.logger import log
from stellapy.walker import find_config_file

YAML_SCHEMA_TEXT = "# yaml-language-server: $schema=https://raw.githubusercontent.com/shravanasati/stellapy/master/schema.json \n"


def get_json_schema() -> dict[str, Any]:
    ref = importlib.resources.files("stellapy").parent / "schema.json"
    with importlib.resources.as_file(ref) as jsonschema_path:
        with open(str(jsonschema_path)) as f:
            return json.load(f)


class ConfigFileNotFound(Exception):
    """
    This exception is raised when the config file (`stella.yml` or a provided one) is not found.
    """

    pass


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
    poll_interval: float  # milliseconds
    browser_wait_interval: float
    scripts: list[Script]

    @classmethod
    def default(cls):
        return cls(
            browser="firefox",
            include_only=[],
            scripts=[Script("default", "", "echo 'hello'", True)],
            poll_interval=500,
            browser_wait_interval=1000,
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

    def find_script(self, script_name: str):
        script_name = script_name.lower()
        for script in self.scripts:
            if script.name.lower() == script_name:
                return script

        return None


class ConfigurationManager:
    """
    Base class for stella'a configuration related tasks.
    """

    def __init__(self, config_file: str | None = None) -> None:
        """
        Constructs the `Configuration` class.
        """
        self.config_file: str | None = None

        # * if a config file is given use it
        if config_file:
            if os.path.exists(config_file):
                self.config_file = config_file
            else:
                raise ConfigFileNotFound(
                    f"The config file `{config_file}` doesn't exist."
                )
        else:
            self.config_file = find_config_file()

        if not self.config_file:
            # self.config_file = os.path.join(os.path.expanduser("~"), "stella.yml")
            raise ConfigFileNotFound(
                f"unable to find `stella.yml` in `{os.getcwd()}` or its parents. try running `stella init`."
            )

        # if not os.path.exists(self.config_file):
        #     self.config = Configuration.default()
        #     with open(self.config_file, "w") as f:
        #         f.write(self.config.to_yaml())

        else:
            with open(self.config_file) as f:
                fc = f.read()
            self.__config = Configuration.from_yaml(fc)

    def load_configuration(self) -> Configuration:
        validate(
            instance=asdict(self.__config),
            schema=get_json_schema(),
            cls=Draft6Validator,
        )
        return self.__config


def load_configuration_handle_errors(
    config_file: str | None,
) -> tuple[str, Configuration]:
    """
    Uses the `ConfigurationManager` to attempt to load configuration, while handling all exceptions
    that are raised by the same, and alerting user.

    Returns the config file being used as well as the `Configuration`.
    """
    config = None
    config_manager = None
    IMPROPER_CONFIG_HELP_TEXT = """
    the config file is corrupted/doesn't have enough or proper parameters.
    1. refer to the config file documentation at https://github.com/shravanasati/stellapy#readme
        or
    2. edit stella.yml file using hints given by yaml language server in the IDE of your choice
        or
    3. remove existing stella.yml and run `stella init`
    """
    try:
        config_manager = ConfigurationManager(config_file)
        config = config_manager.load_configuration()
    except ConfigFileNotFound as cfe:
        log("error", str(cfe))
        exit(1)
    except TypeError:
        log(
            "error",
            IMPROPER_CONFIG_HELP_TEXT,
        )
        exit(1)
    except ValidationError as ve:
        log(
            "error",
            f"{IMPROPER_CONFIG_HELP_TEXT}\nvalidation error: {ve}",
        )
        exit(1)
    except Exception as e:
        log("error", "fatal: an unknown error occcured")
        exception(e)
        exit(1)

    if not config or not config_manager:
        log("error", "unable to load config -> this should never happen")
        exit(1)

    return str(config_manager.config_file), config


if __name__ == "__main__":
    # print(Configuration.from_yaml(Configuration.default().to_yaml()))
    cm = ConfigurationManager()
    print(cm.config_file)
    print(cm.__config.find_script("default"))
