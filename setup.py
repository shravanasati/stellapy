
from setuptools import find_packages, setup

VERSION = '1.0.0'
with open("README.md") as f:
    README = f.read()

setup(
    name = "stellapy",
    version = VERSION,
    description = "Project summary here",
    long_description_content_type = "text/markdown",
    long_description = README,
    url = "https://github.com/Shravan-1908/stellapy",
    author = "Shravan Asati",
    author_email = "Your email here",
    packages = find_packages(),
    install_requires = [],
    license = 'MIT',
    keywords = [],
    classifiers = []
)
