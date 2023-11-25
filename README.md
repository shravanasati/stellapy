# stella

![stella_demo](assets/stella.gif)

[![Downloads](https://pepy.tech/badge/stellapy)](https://pepy.tech/project/stellapy)

stella is a command line utility made for streamlining web development experience. 
It is able to reload server as well as the browser page on every file change.
Although you can use it like any other live reload tool - with builtin `.gitignore` detection and following, along with several other features like multiple command execution, and the npm-scripts like interface.

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

I wanted a CLI that could live reload the browser page as well as live restart the server. I tried to find such a tool, but didn't find one. So I made stella - that could reload backend as well as frontend code. Also the builtin debug modes of web frameworks sucked.

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

This yaml file comes with a schema which can be utilized by yaml language servers to provide autocompletion and validation to make sure the config is correct.

### Configuration

Let's quickly go over the config options:

 - **`browser`**: This option specifies the browser to use when `url` is given. The only valid options for browser currently are `firefox` and `chrome`.

 - **`include_only`**: The list of gitignore-style patterns to consider for live reload. This will be used along with the ignore file (`stella.ignore` or `.gitignore`) to match files. eg. `include_only: ["*.py", "*.env"]`.

 - **`poll_interval`**: The duration in **milliseconds** to poll the filesystem for changes.

 - **`browser_wait_interval`**: This is the duration in **milliseconds** between the execution of given command on the terminal and browser page refresh. This can be used in situations when the server takes some time before it is ready to listen on a given port.

 - **`follow_symlinks`**: Boolean value that indicates whether to follow symbolic links encountered in the filesystem.

 - **`scripts`**: This the list of npm style scripts that take 4 parameters each.

    * `name`: Name of the script. To execute a certain script, use its name in the `stella run SCRIPT_NAME` command. The script named _default_ will be used in case SCRIPT_NAME is not provided.

    * `url`: The URL to listen to on the browser. Set it to an empty string (`''`) if you don't want live reload on the browser. eg. `localhost:8000`.

    * `command`: A single command or a list of commands to execute on the terminal. eg.
      ```
      command: python3 app.py
      ```

      ```
      command: 
        - go fmt ./...
        - go build
        - ./main.exe
      ```
      If a list of commands are provided, the `shell` will be considered `true` even if it's `false`.

    * `shell`: **Boolean** value which indicates whether to execute commands inside a shell context (like bash, powershell, zsh...) or as an independent process. This is useful if you want to execute shell scripts directly without invoking the shell interpreter. On Windows, powershell is used as shell (instead of cmd). On Linux and MacOS, the shell used is determined by `SHELL` environment variable. If it's not present, `/bin/sh` will be used.


### Ignore

Polling a filesystem for changes can be lengthy in case of big projects.
Even worse when dependencies are vendored within the project, like python virtual environments or include directories in c/c++.

Therefore, you can create a `stella.ignore` file in the project with gitignore-style patterns to exclude certain directories and files to consider.

Otherwise, `.gitignore` also just works, and is the recommended way.

However, `stella.ignore` will be the first one that will be searched for. If it's not found, stella will resort to `.gitignore`.

Ignore patterns are cached once stella is started, similar to the stella configuration. If you change either of them, in order to see the desired changes, you need stop stella and run it again.


### run

```
stella run SCRIPT_NAME
stella run SCRIPT_NAME --config-file /path/to/config/stella.yml
```

The `run` command is used to start stella.
It expects one optional argument: the script name to run from the config file.

An optional `--config-file` (`-c` for short) flag can be used to specify the config file to be used. 
Alternatively, an environment variable named `STELLA_CONFIG` can be set for the same.

If not provided, stella will attempt to find `stella.yml` in the current directory or its parent folders until its found.


While stella is running, you can input `rs` to restart the server and refresh the browser page manually, and `rb` only to refresh the browser page.

To stop stella, input `ex`. It will close the browser as well as kill the running process gracefully.

<br>


## 📄 Licensing

License © 2021-Present Shravan Asati

This repository is licensed under the MIT license. See [LICENSE](LICENSE) for details.

<br>

## 👥 Contribution

Contribution is more than welcome. For more guidelines on contributing to stella, refer [CONTRIBUTING.md](CONTRIBUTING.md).