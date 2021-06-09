from logger import log
from walker import walk, get_file_content
from time import sleep
from executor import Executor
import helium

# TODO manual restart and exit of server

class Reloader():
    """
    The `Reloader` class.
    """
    def __init__(self, command:str) -> None:
        self.project_data = self.get_project_data()
        self.ex = Executor(command)


    def get_project_data(self) -> dict:
        """
        Returns a dict with filenames mapped to their contents.
        """
        project_data = {}
        for f in walk():
            project_data.update({f: get_file_content(f)})
        
        return project_data

    def detect_change(self) -> bool:
        """
        Detects if a change has been done to the project. Also updates the project data if
        new a change is detected.
        """
        new_content = self.get_project_data()
        if len(self.project_data.keys()) != len(new_content.keys()):
            self.project_data = new_content
            return True

        try:
            for k, v in self.project_data.items():
                if new_content[k] != v:
                    self.project_data = new_content
                    return True

        except KeyError:
            self.project_data = new_content
            return True

        except Exception as e:
            print("FATAL ERROR: This should never happen.")
            print(e)
            quit(1)

        return False


    def reload(self) -> None:
        helium.start_firefox("localhost:5000")
        while True:
            # print(self.detect_change())
            if self.detect_change():
                log("info", "detected changes in the project, reloading server and browser")
                self.ex.re_execute()
                sleep(1)
                helium.refresh()

            else:
                sleep(1)

    def start_server(self) -> None:
        """
        Starts the server. All reloading and stuff is done here.
        """
        log("stella", "starting stella")
        self.ex.start()
        self.reload()

if __name__ == "__main__":
    r = Reloader("python3 ./test.py")
    r.start_server()