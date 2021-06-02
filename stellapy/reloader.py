from walker import Walker
from time import sleep
import subprocess

# TODO manual restart and exit of server

class Reloader():
    """
    The `Reloader` class.
    """
    def __init__(self) -> None:
        self.w = Walker()
        self.project_data = self.get_project_data()

    def get_project_data(self) -> dict:
        """
        Returns a dict with filenames mapped to their contents.
        """
        project_data = {}
        for f in self.w.walk():
            project_data.update({f: self.w.get_file_content(f)})
        
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
            for k, v in self.project_data:
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

    def reload(self, command:str) -> None:
        while True:
            if self.detect_change():
                subprocess.run(command)

            else:
                sleep(1)