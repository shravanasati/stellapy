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
        self.__command = self.build_command(script)
        self.shell = script.shell
        # print(self.__command, self.shell)

    @staticmethod
    def build_command(script: Script):
        if isinstance(script.command, str):
            return shlex.split(script.command)
        elif isinstance(script.command, list):
            return " && ".join(script.command)
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
                    shell=self.shell
                )
            else:
                self.__process = subprocess.Popen(
                    self.__command,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    preexec_fn=os.setsid,  # type: ignore (unix based systems)
                    shell=self.shell
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
            log("error", "the app crashed, waiting for file changes to restart...")
            print(e)


# if __name__ == "__main__":
#     import time
#     e = Executor("python3 ./test.py")
#     e.start()
#     time.sleep(15)
#     e.re_execute()
#     time.sleep(15)
#     e.close()
