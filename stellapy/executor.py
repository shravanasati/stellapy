import sys
import subprocess
import os
import signal
import shlex

class Executor():
    """
    base class for executing sys calls.
    """
    def __init__(self, command:str) -> None:
        self.__command = shlex.split(command)

    def start(self):
        self.__process = subprocess.Popen(self.__command, stdout=sys.stdout, stderr=sys.stderr, preexec_fn=os.setsid)

    def re_execute(self):
        self.close()
        self.__process = subprocess.Popen(self.__command, stdout=sys.stdout, stderr=sys.stderr, preexec_fn=os.setsid)

    def close(self):
        os.killpg(os.getpgid(self.__process.pid), signal.SIGTERM)

# if __name__ == "__main__":
#     import time
#     e = Executor("python3 ./test.py")
#     e.start()
#     time.sleep(15)
#     e.re_execute()
#     time.sleep(15)
#     e.close()
