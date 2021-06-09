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
        self.__process = subprocess.Popen(self.__command, stdout=sys.stdout, stderr=sys.stderr)

    def re_execute(self):
        self.__process.terminate()
        self.__process = subprocess.Popen(self.__command, stdout=sys.stdout, stderr=sys.stderr)

    def close(self):
        self.__process.terminate()

# if __name__ == "__main__":
#     import time
#     e = Executor("python3 ./test.py")
#     e.start()
#     time.sleep(15)
#     e.re_execute()
#     time.sleep(15)
#     e.close()
