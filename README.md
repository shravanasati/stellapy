# stella

![stella_demo](assets/stella.gif)

[![Downloads](https://pepy.tech/badge/stellapy)](https://pepy.tech/project/stellapy)

stella is a command line utility made for streamlining web development experience. It is able to reload server as well as the browser page on every file change.

<br>


## 📝 Table of Contents
- [Installation](#%EF%B8%8F-installation)
- [Motivation](#-motivation)
- [How does stella work?](#%EF%B8%8F-how-does-stella-work)
- [Usage](#-usage)
- [Changelog](#-changelog)
- [Versioning](#-versioning)
- [Licensing](#-licensing)
- [Contribution](#-contribution)


<br>


## ⚡️ Installation

Using [pipx](https://pypa.github.io/pipx/) (recommended):
```
pipx install stellapy
```

On Windows:
```
pip install stellapy
```

On Linux/MacOS:
```
pip3 install stellapy
```


<br>



## 💫 Motivation

I wanted a CLI that could live reload the browser page as well as live restart the server. I tried to find such a tool, but didn't find one. So I made stella - that could reload backend as well as frontend code. Also the builtin debug modes for web frameworks sucked.

<br>

## ⚙️ How does stella work?

stella continuously watches for file changes in the project, while respecting the gitignore file and whenever a change is made, it kills the existing process and spawns a new process using subprocess. What about browser reload? It uses selenium to accomplish that.

<br>


## 💡 Usage

This section briefly describes how to use the stella CLI.

### init

```
stella init
```

The `init` command writes a default `stella.yml` config file in the working directory. The default configuration looks like this:

```yml
# yaml-language-server: $schema=https://raw.githubusercontent.com/Shravan-1908/stellapy/master/schema.json 
browser: firefox
include_only: []
poll_interval: 500
browser_wait_interval: 1000
follow_symlinks: false
scripts:
- name: default
  url: ''
  command: echo 'hello'
  shell: true
```

This yaml file comes with a schema

<!-- todo describe config file, how stella finds it -->
<!-- todo stella.ignore file -->


### run

```
stella run SCRIPT_NAME
```

The `run` command is used to start stella.
It expects one optional argument: the script name to run from the config file.


While stella is running, you can input `rs` to restart the server and refresh the browser page manually, and `rb` only to refresh the browser page.

To stop stella, input `ex`. It will close the browser as well as kill the running process gracefully.


<br>


## ⏪ Changelog
The changes made in the latest version of *stella*, v0.1.0 are:

- Initial release

View [CHANGELOG.md](CHANGELOG.md) for more information.

<br>


## 🔖 Versioning

stella releases follow semantic versioning, every release is in the *x.y.z* form, where:

- x is the MAJOR version and is incremented when a backwards incompatible change to stella is made.
- y is the MINOR version and is incremented when a backwards compatible change to stella is made, like changing dependencies or adding a new function, method, or features.
- z is the PATCH version and is incremented after making minor changes that don't affect stella's public API or dependencies, like fixing a bug.

<br>

## 📄 Licensing

License © 2021-Present Shravan Asati

This repository is licensed under the MIT license. See [LICENSE](LICENSE) for details.

<br>

## 👥 Contribution

Contribution is more than welcome. For more guidelines on contributing to stella, refer [CONTRIBUTING.md](CONTRIBUTING.md).