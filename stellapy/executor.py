import os
import shlex
import signal
import subprocess
import sys
from platform import system

from stellapy.logger import log

WIN = system() == "Windows"


class Executor:
    """
    base class for executing sys calls.
    """

    def __init__(self, command: str) -> None:
        self.__command = shlex.split(command)

    def start(self):
        try:
            if WIN:
                self.__process = subprocess.Popen(
                    self.__command,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                )
            else:
                self.__process = subprocess.Popen(
                    self.__command,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    preexec_fn=os.setsid,
                )
        except Exception as e:
            log("error", "the app crashed, waiting for file changes to restart...")
            print(e)

    def re_execute(self):
        self.close()
        self.start()

    def close(self):
        try:
            if WIN:
                self.__process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(os.getpgid(self.__process.pid), signal.SIGTERM)
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
