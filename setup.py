from setuptools import find_packages, setup

VERSION = "0.1.1"
with open("README.md") as f:
    README = f.read()

setup(
    name = "stellapy",
    version = VERSION,
    description = "Streamline your web dev experience with stella.",
    long_description_content_type = "text/markdown",
    long_description = README,
    url="https://github.com/Shravan-1908/stellapy",
    author = "Shravan Asati",
    author_email = "dev.shravan@protonmail.com",
    packages = find_packages(),
    install_requires = ["click", "helium"],
    license = 'MIT',
	entry_points = '''
	[console_scripts]
	stella=stellapy.stella:main
	''',
    keywords = ["web dev", "development", "website", "python", "cli", "stella", "reloader", "walker", "executor", "helium", "selenium", "automation"],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)