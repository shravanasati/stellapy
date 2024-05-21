import os
import shlex
import signal
import subprocess
import sys
from platform import system

from stellapy.configuration import Script
from stellapy.logger import log

WINDOWS = system() == "Windows"


def _test_powershell() -> bool:
    """
    Returns `True` if powershell is available on the system.
    """
    dummy_stdout = open(os.devnull, "w")
    try:
        subprocess.run(
            shlex.split("powershell -h"), stdout=dummy_stdout, stderr=dummy_stdout
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    finally:
        if dummy_stdout:
            dummy_stdout.close()


PWSH_PRESENT = _test_powershell()


class Executor:
    """
    base class for executing processes.
    """

    def __init__(self, script: Script) -> None:
        self.__command, self.shell = self.build_command(script)
        self.command_to_display = (
            self.__command
            if isinstance(self.__command, str)
            else " ".join(self.__command)
        )
        # print(self.__command, sel.shell)

    @staticmethod
    def build_command(script: Script):
        """
        Builds a command based on several different configurations, and returns the command and the
        (boolean type) shell.

        This is a lot of spaghetti code so here's the explanation:

        1. If script.command is a str
            a. If powershell is available and on Windows
                i. script.shell==True
                    return shlex splitted (powershell command) and shell as it is(=True)
                ii. script.shell==False
                    return shlex splitted command and shell as it is(=False)
            b. If powershell is not available
                whether windows(pwsh not present) or unix
                return shlex splitted command and shell as it is

        2. If script.command is a list comprising of only one item
        Here we want DO NOT want to execute as shell (which is the default behaviour if command is a list)
        we want to execute as case 1 only, with the caveat of script.command[0] instead of script.command

        3. If script.command is a list (>1 elements)
        We want to execute with shell=True since multiple command execution is achieved using command
        chaining which is a shell feature.
        We first decide the command chainer character:
            A. pwsh -> ;
            B. cmd.exe -> &
            C. unix -> &&

        Then the command building logic is as follows:
            a. windows and powershell present
                return (powershell joined) command, and True
            b. windows and powershell NOT present
                return joined command, and True
            c. unix
                return joined command, True

        This is because with shell=True, python will handle cmd.exe and unix case by itself.
        For powershell we need `powershell -Command '{joined_command}'`.

        4. Raise a type error because we don't identify the command type.
        """
        if isinstance(script.command, str):
            if PWSH_PRESENT and WINDOWS:
                return (
                    shlex.split(
                        f"powershell -Command {script.command}"
                        if script.shell
                        else script.command
                    ),
                    script.shell,
                )
            else:
                # in case of cmd.exe and unix
                return (shlex.split(script.command), script.shell)

        elif isinstance(script.command, list) and len(script.command) == 1:
            # no need to chain commands in this case
            if PWSH_PRESENT and WINDOWS:
                return (
                    shlex.split(
                        f"powershell -Command {script.command[0]}"
                        if script.shell and WINDOWS
                        else script.command[0]
                    ),
                    script.shell,
                )
            else:
                # in case of cmd.exe and unix
                return shlex.split(script.command[0]), script.shell

        elif isinstance(script.command, list):
            # command chaining in powershell is done using ';', and '&&' on posix systems
            chainer_sep = "; " if WINDOWS else " && "
            if WINDOWS and (not PWSH_PRESENT):
                chainer_sep = " & "  # chainer for cmd.exe
            joined_command = chainer_sep.join(script.command)
            if WINDOWS and PWSH_PRESENT:
                return f'powershell -Command "{joined_command}"', True
            elif WINDOWS and (not PWSH_PRESENT):
                return joined_command, True
            else:
                return joined_command, True

        else:
            raise TypeError(
                f"invalid type of {script.command=}, {type(script.command)=}"
            )

    def start(self):
        try:
            if WINDOWS:
                self.__process = subprocess.Popen(
                    self.__command,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    shell=False if PWSH_PRESENT else True,
                    # setting shell False if we want to execute commands using pwsh,
                    # if pwsh not available, use cmd.exe as fallback, which is done by python
                )
            else:
                self.__process = subprocess.Popen(
                    self.__command,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    preexec_fn=os.setsid,  # type: ignore (unix based systems)
                    shell=self.shell,
                )
        except Exception as e:
            log("error", "the app crashed, waiting for file changes to restart...")
            print(e)

    def re_execute(self):
        self.close()
        self.start()

    def close(self):
        try:
            if WINDOWS:
                self.__process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(os.getpgid(self.__process.pid), signal.SIGTERM)  # type: ignore
        except Exception as e:
            print(e)
            log("error", "the app crashed, waiting for file changes to restart...")


if __name__ == "__main__":
    print(_test_powershell())
    # import time
    # e = Executor("python3 ./test.py")
    # e.start()
    # time.sleep(15)
    # e.re_execute()
    # time.sleep(15)
    # e.close()
