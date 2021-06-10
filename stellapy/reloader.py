import os
from logger import log
from walker import walk, get_file_content
from time import sleep
from executor import Executor
import helium
from threading import Thread

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


    def restart(self) -> None:
        # * checking for browser
        try:
            helium.start_chrome("localhost:5000")
        except Exception: 
            log("error", "Chrome binary not found, trying with firefox...")
            try:
                helium.start_firefox("localhost:5000")
            except Exception:
                log("error", "Firefox binary also not found, install either chrome or firefox on your system.")
                self.ex.close()
                quit(-1)


        while True:
            try:
                if self.detect_change():
                    log("info", "detected changes in the project, reloading server and browser")
                    self.ex.re_execute()
                    sleep(1)
                    helium.refresh()

                else:
                    sleep(1)

            except Exception:
                try:
                    log("error", "Browser reload didnt work, retrying in 5 seconds...")
                    sleep(5)
                    helium.refresh()
                except Exception:
                    log("error", "Browser reload retry failed!")
                    self.stop_server()

    def manual_input(self) -> None:
        """
        Manual restart and exit.
        """
        while True:
            message = input().lower().strip()
            if message == "ex":
                log("info", "stopping server")
                self.stop_server()

            elif message == "rs":
                log("info", "restarting the server")
                self.ex.re_execute()
                sleep(1)
                helium.refresh()

    def stop_server(self):
        try:
            self.ex.close()
            helium.kill_browser()
        except Exception as e:
            log("error", "An error occured while stopping the server, this should never happen.")
            print(e)
        finally:
            os._exit(0)

    def start_server(self) -> None:
        """
        Starts the server. All reloading and stuff is done here.
        """
        log("stella", "starting stella")
        log("stella", "input `rs` manually to restart the server and `ex` to stop the server")
        input_thread = Thread(target=self.manual_input)
        input_thread.start()
        self.ex.start()
        self.restart()

if __name__ == "__main__":
    r = Reloader("python3 ./test.py")
    r.start_server()