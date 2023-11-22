import os
from logging import exception

import click

from stellapy.configuration import (ConfigFileNotFound, Configuration,
                                    ConfigurationManager)
from stellapy.logger import log
from stellapy.reloader import Reloader

NAME = "stella"
VERSION = "0.2.0"

# , help = "The url to listen to on the browser. Example: localhost:5000", prompt = "Enter the URL to listen to on the browser"
# , help = "The command to execute on a file change. Example: python3 app.py", prompt = "Enter the command to execute on a file change"


@click.group("stella")
@click.version_option(VERSION, prog_name=NAME)
def main():
    """
    stella is a command line utility made to streamline your web development experience, by
    providing reload capabilities for both the backend as well as the frontend code.

    Visit https://github.com/Shravan-1908/stellapy for more info.

    Example Usage:

    $ stella run 'python3 app.py' localhost:5000

    $ stella config --browser firefox
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
def run(script: str, config_file: str):
    """
    Run the server with stella. Expects two optional arguments - the command to execute or the name
    of the script and the URL to listen at on the browser.\n
    If no argument is provided, stella will run the script named default from the config file.

    You can also pass a --config-file option pointing to the path of the config file to be used. Alternatively,
    an environment variable named `STELLA_CONFIG` can also be set for the same.
    This is generally not required since stella automatically attempts to find `stella.yml` file in the
    current directory and its parents.

    Example:\n
    $ stella run  // runs the default script from config \n
    $ stella run [script_name]  // runs the given script from config \n
    $ stella run 'node index.js' localhost:8000  // in case you don't want to use config file
    """
    config = None
    try:
        config_manager = ConfigurationManager(config_file)
        config = config_manager.load_configuration()
    except ConfigFileNotFound as cfe:
        log("error", str(cfe))
        exit(1)
    except TypeError:
        log(
            "error",
            "the config file is corrupted/doesn't have enough parameters. \n 1 refer to the config file documentation at https://github.com/Shravan-1908/stellapy#readme \n or \n 2. edit stella.yml file using hints given by yaml language server in the IDE of your choice \n or \n 3. remove existing stella.yml and run `stella init`",
        )
        exit(1)

    if not config:
        log("error", "unable to load config -> this should never happen")
        exit(1)

    r = Reloader(
        config, script, config_file if config_file else str(config_manager.config_file)
    )
    r.start_server()


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
            "unable to write stella.yml file in the current directory: not enough persmissions",
        )

    except Exception as e:
        log("error", "an unknown error occured!")
        exception(e)


if __name__ == "__main__":
    main()
