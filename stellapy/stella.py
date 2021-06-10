import click
from stellapy.reloader import Reloader
# , help = "The url to listen to on the browser. Example: localhost:5000", prompt = "Enter the URL to listen to on the browser"
# , help = "The command to execute on a file change. Example: python3 app.py", prompt = "Enter the command to execute on a file change"
@click.command()
@click.argument("command", required=True)
@click.argument("url", required=True)
def main(command, url):
	"""
	stella is a command line utility made to streamline your web development experience.
	Visit https://github.com/Shravan-1908/stellapy for more info.
	"""
	r = Reloader(command, url)
	r.start_server()
