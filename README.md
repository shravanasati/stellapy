# stella

![stella_demo](assets/stella.gif)

stella is a command line utility made for streamlining web development experience. It is able to reload server as well as browser on every file change.

<br>


## 📝 Table of Contents
- [Installation](#-installation)
- [Motivation](#-motivation)
- [How does stella work?](#-how-does-stella-work?)
- [Usage](#-usage)
- [Changelog](#-changelog)
- [Versioning](#-versioning)
- [Licensing](#-licensing)
- [Contribution](#-contribution)


<br>


## ⚡️ Installation

On Windows:
```
pip install stellapy
```

On Linux/MacOS:
```
pip3 install stellapy
```

Or if you're using [pipx](https://pypa.github.io/pipx/):
```
pipx install stellapy
```


<br>



## 💫 Motivation

I wanted a CLI that could reload the browser for static content as well as restart the server for the dynamic content. I tried to find such a tool, but didn't find one. So I made stella - that could reload backend as well as frontend code.

<br>

## ⚙️ How does stella work?

stella continuously watches for file changes in the project (html, css, js, py, rb, go, rs, php, java) and whenever a change is made, it kills the existing process and spawns a new process using subprocess. What about browser reload? It uses selenium to accomplish browser reload.

<br>


## 💡 Usage

This section briefly describes how to use the stella CLI.

### config

```
stella config {options}
```

The `config` command is used to configure stella. The only option for *v0.1.0* is browser. When stella is ran for the first time, it automcatically configures chrome as the browser to start and perform reload actions on. However, if you want stella to use firefox, execute:

```
stella config --browser=firefox
```

### run

```
stella run COMMAND URL
```

The `run` command is used to start stella.
It expects two arguments:

1. `command` --> The shell command to execute on every file reload. Example:
`python3 app.py`.

2. `url` --> The URL to listen at the browser. Whenever a file is changed, stella will execute the shell command provided and then reload the browser. Example: `localhost:5000`.

Example:
```
stella run "python3 app.py" localhost:5000
```

While stella is running, you can input `rs` to restart the server and reload the browser again. 

To stop stella, input `ex`. It will close the browser as well as kill the running process gracefully.

**It is strongly recommended to not to stop stella abruptly by pressing Ctrl+C. This will keep the process running in the background, which might create problems for you.**

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