import sys
import subprocess
from logger import log

class Executor():
    """
    base class for executing sys calls.
    """
    def __init__(self, command:str) -> None:
        self.__command = command.split(' ')
        
    def start(self):
        log("stella", "starting")
        self.__process = subprocess.Popen(self.__command, stdout=sys.stdout, stderr=sys.stderr)

    def re_execute(self):
        log("stella", "re executing")
        self.__process.terminate()
        self.__process = subprocess.Popen(self.__command, stdout=sys.stdout, stderr=sys.stderr)

    def close(self):
        log("stella", "closing")
        self.__process.terminate()

if __name__ == "__main__":
    import time
    e = Executor("python3 ./test.py")
    e.start()
    time.sleep(15)
    e.re_execute()
    time.sleep(15)
    e.close()
