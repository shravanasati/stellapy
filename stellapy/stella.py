import click
from stellapy.reloader import Reloader
from stellapy.configuration import Configuration

NAME = "stella"
VERSION = "0.1.0"

# , help = "The url to listen to on the browser. Example: localhost:5000", prompt = "Enter the URL to listen to on the browser"
# , help = "The command to execute on a file change. Example: python3 app.py", prompt = "Enter the command to execute on a file change"


@click.group("stella")
@click.version_option(VERSION, prog_name=NAME)
def main():
    """
    stella is a command line utility made to streamline your web development experience.
    Visit https://github.com/Shravan-1908/stellapy for more info.
    """
    pass

@main.command("run")
@click.argument("command", required = True)
@click.argument("url", required = True)
def run(command, url):
	"""
	Run the server with stella. Expects two arguments - the command to execute and the URL to listen at on the browser.
	"""
	r = Reloader(command, url)
	r.start_server()


@main.command("config")
@click.option("--browser", default = "chrome")
def config(browser):
	"""
	Configure stella for a personalised experience.
	"""
	c = Configuration()
	config = c.load_configuration()
	config["browser"] = browser
	c.set_configuration(config)

if __name__ == "__main__":
	main()