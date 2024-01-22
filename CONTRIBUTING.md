# Contributing to stella

👍🎉 First off, thanks for taking the time to contribute! 🎉👍

The following is a set of guidelines for contributing to *stella*, which is hosted on GitHub. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.


## Project Structure
```
├── .github
|  ├── ISSUE_TEMPLATE
|  |  ├── bug_report.md
|  |  ├── config.yml
|  |  ├── custom.md
|  |  └── feature_request.md
|  └── workflows
|     └── python-package.yml
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── assets
├── requirements.txt
├── setup.py
├── stellapy
|  ├── __init__.py
|  ├── configuration.py
|  ├── executor.py
|  ├── logger.py
|  ├── reloader.py
|  ├── stella.py
|  └── walker.py
```

## Setup Development Environment
This section shows how you can setup your development environment to contribute to stella.

- Fork the repository.
- Clone it using Git (`git clone https://github.com/<YOUR USERNAME>stella.git`).
- Create a new git branch (`git checkout -b "BRANCH NAME"`).
- Execute `pip install -e .` to install all the dependencies and make an editable install.
- Make changes.
- Stage and commit (`git add .` and `git commit -m "COMMIT MESSAGE"`).
- Push it your remote repository (`git push`).
- Open a pull request by clicking [here](https://github.com/shravanasati/stellapy/compare).


## Reporting Issues
If you know a bug in the code or you want to file a feature request, open an issue.
Choose the correct issue template from [here](https://github.com/shravanasati/stellapy/issues/new/choose).