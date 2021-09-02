from pathlib import Path
import requests
import helium
from stellapy.configuration import Configuration
from stellapy.logger import log

# TODO fix browser compatibility issues
# TODO add a check for the existence of the config file
# TODO check if the config file is valid

class Doctor:
	"""
	base class for the stella doctor, which fixes the browser-webdriver incompatibility issues.
	"""
	def __init__(self):
		log("info", "running the stella doctor")
		self.config = Configuration().load_configuration()

	def _check_compatibility(self) -> bool:
		"""
		checks compatibility of the browser and the webdriver.
		"""
		browser = self.config.get('browser')

		try:
			if browser == "chrome":
				driver = helium.start_chrome()

				browser_version = driver.capabilities['browserVersion']
				driver_version =  driver.capabilities['chrome']['chromedriverVersion']
				driver.quit()

				if browser_version[:2] != driver_version[:2]:
					return False

				return True

			else:
				log("info", "doctor support is only available for chrome at the moment.")
				return True

		except Exception as e:
			log("error", "an unknown error occurred: " + str(e))

	def main(self):
		"""
		Main doctor command.
		"""
		if not self._check_compatibility():
			log("error", "browser error")

		else:
			log("info", "everything's alright!")

if __name__ == "__main__":
	Doctor()._check_compatibility()