import os
from threading import Thread
from time import sleep

import helium

from stellapy.configuration import Configuration
from stellapy.executor import Executor
from stellapy.logger import log
from stellapy.walker import get_file_content, walk


class Reloader:
    """
    The `Reloader` class.
    """

    def __init__(self, command: str, url: str | None) -> None:
        self.project_data = self.get_project_data()
        self.command = command
        self.executor = Executor(self.command)
        self.url = url
        self.RELOAD_BROWSER = bool(self.url)
        c = Configuration()
        self.config = c.load_configuration()

    @staticmethod
    def get_project_data() -> dict:
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

    def start_browser(self):
        browser = self.config["browser"]
        if browser == "chrome":
            try:
                helium.start_chrome(self.url)
            except Exception as e:
                if "Message: unknown error: cannot find Chrome binary" in str(e):
                    log(
                        "error",
                        "chrome binary not found. either install chrome browser or configure stella browser to firefox.",
                    )
                    self.stop_server()

                elif "Reached error page" in str(e):
                    log("error", "app crashed, waiting for file changes to restart...")

                else:
                    log("error", f"an unknown error occurred: \n{e}")
                    self.stop_server()

        elif browser == "firefox":
            try:
                helium.start_firefox(self.url)
            except Exception as e:
                if "Message: unknown error: cannot find Firefox binary" in str(e):
                    log(
                        "error",
                        "firefox binary not found. either install chrome browser or configure stella browser to firefox.",
                    )
                    self.stop_server()

                elif "Message: Reached error page" in str(e):
                    log("error", "app crashed, waiting for file changes to restart...")

                else:
                    log("error", f"an unknown error occurred: \n{e}")
                    self.stop_server()

        else:
            log(
                "error",
                f"invalid browser specified: {browser}. stella supports only chrome and firefox. execute `stella config --browser chrome|firefox` for configuring the browser.",
            )
            self.stop_server()

    def _restart(self):
        try:
            if self.detect_change():
                log(
                    "info",
                    "detected changes in the project, reloading server and browser",
                )
                self.executor.re_execute()
                sleep(1)
                if self.RELOAD_BROWSER:
                    helium.refresh()

            else:
                sleep(1)

        except Exception:
            try:
                log("error", "browser reload didnt work, retrying in 5 seconds...")
                sleep(5)
                if self.RELOAD_BROWSER:
                    helium.refresh()
            except Exception:
                log(
                    "error",
                    "browser reload retry failed! make sure you've provided stella the correct url to listen at. waiting for file changes to restart...",
                )

    def restart(self) -> None:
        if self.RELOAD_BROWSER:
            self.start_browser()
        while True:
            self._restart()

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
                try:
                    self.executor.re_execute()
                    if self.RELOAD_BROWSER:
                        sleep(1)
                        helium.refresh()

                except Exception:
                    try:
                        log(
                            "error",
                            "browser reload didnt work, retrying in 5 seconds...",
                        )
                        sleep(5)
                        if self.RELOAD_BROWSER:
                            helium.refresh()
                    except Exception:
                        log(
                            "error",
                            "browser reload retry failed! make sure you've provided stella the correct url to listen at. waiting for file changes to restart...",
                        )

    def stop_server(self):
        try:
            self.executor.close()
            if self.RELOAD_BROWSER:
                helium.kill_browser()
        except Exception as e:
            log(
                "error",
                "an error occured while stopping the server, this should never happen.",
            )
            print(e)
        finally:
            os._exit(0)

    def start_server(self) -> None:
        """
        Starts the server. All reloading and stuff is done here.
        """
        log("stella", "starting stella")
        # todo log configuration file being used
        log(
            "stella",
            f"executing `{self.command}` and listening at {self.url} on the browser",
        )
        log(
            "stella",
            "input `rs` to manually restart the server and `ex` to stop the server",
        )
        input_thread = Thread(target=self.manual_input)
        input_thread.start()
        self.executor.start()
        self.restart()
