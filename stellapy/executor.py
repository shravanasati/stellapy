import os
import shlex
import signal
import subprocess
import sys
from platform import system
from stellapy.configuration import Script

from stellapy.logger import log

WINDOWS = system() == "Windows"


class Executor:
    """
    base class for executing sys calls.
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
        if isinstance(script.command, str):
            return shlex.split(
                f"powershell -Command {script.command}"
                if script.shell and WINDOWS
                else script.command
            ), script.shell
        elif isinstance(script.command, list) and len(script.command) == 1:
            # no need to chain commands in this case
            return shlex.split(
                f"powershell -Command {script.command[0]}"
                if script.shell and WINDOWS
                else script.command[0]
            ), script.shell
        elif isinstance(script.command, list):
            # command chaining in powershell is done using ';', and '&&' on posix systems
            chainer_sep = "; " if WINDOWS else " && "
            joined_command = chainer_sep.join(script.command)
            if WINDOWS:
                return f'powershell -Command "{joined_command}"', True
            else:
                return joined_command, True
        else:
            raise TypeError(f"invalid type of {script.command=}")

    def start(self):
        try:
            if WINDOWS:
                self.__process = subprocess.Popen(
                    self.__command,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    shell=False,
                    # setting shell False because we want to execute commands using pwsh,
                    # not cmd and that is done above in build_command
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


# if __name__ == "__main__":
#     import time
#     e = Executor("python3 ./test.py")
#     e.start()
#     time.sleep(15)
#     e.re_execute()
#     time.sleep(15)
#     e.close()
