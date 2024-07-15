import os
from logging import exception

import click

from stellapy.configuration import Configuration, load_configuration_handle_errors
from stellapy.logger import log
from stellapy.reloader import Reloader

NAME = "stella"
VERSION = "0.4.0"

# , help = "The url to listen to on the browser. Example: localhost:5000", prompt = "Enter the URL to listen to on the browser"
# , help = "The command to execute on a file change. Example: python3 app.py", prompt = "Enter the command to execute on a file change"


@click.group("stella")
@click.version_option(VERSION, prog_name=NAME)
def main():
    """
    stella is a command line utility made to streamline your web development experience, by
    providing live reload capabilities for both the backend as well as the frontend code.

    Visit https://github.com/shravanasati/stellapy for more info.

    Example Usage:\n
    $ stella init\n
    $ stella run server
    """
    pass


@main.command("run")
@click.argument("script", default="default")
@click.option(
    "--config-file",
    "-c",
    required=False,
    type=str,
    help="Path to the config file that is to be used.",
    envvar="STELLA_CONFIG",
)
def run(script: str, config_file: str | None):
    """
    Run the specified script with stella. Expects one argument - the name of the script from a config
    file. If no argument is provided, stella will run the script named `default` from the config file.

    You can also pass a --config-file option pointing to the path of the config file to be used.
    Alternatively, an environment variable named `STELLA_CONFIG` can also be set for the same.
    This is generally not required since stella automatically attempts to find `stella.yml` file in the
    current directory and its parents.

    Examples: \n
    $ stella run  // runs the default script from config \n
    $ stella run [script_name]  // runs the given script from config \n
    $ stella run [script_name] --config-file /path/to/stella.yml
    """
    config_file_used, config = load_configuration_handle_errors(config_file)
    reloader = None
    try:
        reloader = Reloader(config, script, config_file_used)
        reloader.start()
    except KeyboardInterrupt:
        log("info", "stopping server")
        if reloader:
            reloader.stop()
    except Exception as e:
        log("error", "fatal: unknown error in reloader")
        exception(e)


@main.command("init")
def init():
    """
    Write a default `stella.yml` file in the current working directory, if it doesn't exists.

    Example:\n
    $ stella init
    """
    try:
        if os.path.exists("./stella.yml"):
            log(
                "error",
                "a stella.yml file already exists in the current directory, remove it to run init again.",
            )
            return
        with open("./stella.yml", "w", encoding="utf-8") as f:
            f.write(Configuration.default().to_yaml())
        log("info", "stella.yml file sucessfully written")

    except PermissionError:
        log(
            "error",
            "unable to write stella.yml file in the current directory: not enough permissions",
        )

    except Exception as e:
        log("error", "an unknown error occured!")
        exception(e)


if __name__ == "__main__":
    main()
