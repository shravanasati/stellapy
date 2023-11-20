from logging import exception
import os
import click

from stellapy.configuration import Configuration
from stellapy.reloader import Reloader
from stellapy.logger import log

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
@click.argument("command", required=True)
@click.argument("url", required=False)
def run(command, url):
    """
    Run the server with stella. Expects two arguments - the command to execute and the optional
    URL to listen at on the browser.\n
    Example:\n
    $ stella run 'node index.js' localhost:8000
    """
    r = Reloader(command, url)
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
                "a stella.yml already exists in the current directory, remove it to run init again.",
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


@main.command("config")
@click.option(
    "--browser", "-b", default="chrome", help="Select the browser to listen the URL on."
)
def config(browser):
    """
    Configure stella for a personalized experience.

    Usage:

    $ stella config -b chrome
    """
    c = Configuration()
    config = c.load_configuration()
    config["browser"] = browser
    c.set_configuration(config)


if __name__ == "__main__":
    main()
