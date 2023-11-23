import os
from logging import exception
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

    def __init__(
        self, config: Configuration, script_name: str, config_file: str
    ) -> None:
        """
        Constructs the Reloader class. Sets a lot of instance variables used from the config. The
        `config_file` is the path to the config file.
        """
        self.config = config
        self.script = self.config.find_script(script_name)
        if not self.script:
            log(
                "error",
                f"didn't find any script named {script_name.lower()} in config located at `{config_file}`",
            )
            exit(1)
        self.config_file = config_file
        self.executor = Executor(self.script)
        self.url = self.script.url
        self.RELOAD_BROWSER = bool(self.url)
        self.project_data = self.get_project_data()

        # convert to seconds
        self.poll_interval = self.config.poll_interval / 1000
        self.browser_wait_interval = self.config.browser_wait_interval / 1000

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
            exception(e)
            os._exit(1)

        return False

    def start_browser(self):
        browser = self.config.browser
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
                        "firefox binary not found. either install chrome browser or configure stella to use firefox.",
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
                sleep(self.browser_wait_interval)
                if self.RELOAD_BROWSER:
                    helium.refresh()

            else:
                sleep(self.poll_interval)
        except Exception:
            try:
                log(
                    "error",
                    f"browser reload didnt work, retrying in {2 * self.browser_wait_interval} seconds...",
                )
                sleep(2 * self.config.browser_wait_interval)
                if self.RELOAD_BROWSER:
                    helium.refresh()
            except Exception:
                log(
                    "error",
                    "browser reload retry failed! make sure you've provided stella the correct url to listen at. waiting for file changes or `rb`/`rs` input to restart...",
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
            try:
                message = input().lower().strip()
            except EOFError:
                break
            if message == "ex":
                log("info", "stopping server")
                self.stop_server()

            elif message == "rs":
                log("info", "restarting the server")
                try:
                    self.executor.re_execute()
                    if self.RELOAD_BROWSER:
                        sleep(self.browser_wait_interval)
                        helium.refresh()

                except Exception:
                    try:
                        log(
                            "error",
                            f"browser reload didnt work, retrying in {2 * self.browser_wait_interval} seconds...",
                        )
                        sleep(2 * self.browser_wait_interval)
                        if self.RELOAD_BROWSER:
                            helium.refresh()
                    except Exception:
                        log(
                            "error",
                            "browser reload retry failed! make sure you've provided stella the correct url to listen at. waiting for file changes or `rb`/`rs` input to restart...",
                        )

            elif message == "rb":
                if self.RELOAD_BROWSER:
                    try:
                        log("info", "trying to reload browser window")
                        helium.refresh()
                    except Exception:
                        log("error", "unable to refresh browser window")
                else:
                    log("stella", "no browser URL is configured, can't refresh")

            # ! too much black magic required to have configuration reloaded
            # ! it's because stop_server calls os._exit and that stops the entire progam because there
            # ! is no way to gracefully stop the input thread
            # ? maybe use timeout input or process
            # elif message == "rc":
            #     log(
            #         "stella",
            #         "attempting to reload configuration, stopping existing commands and browser windows",
            #     )
            #     self.stop_server()
            #     cfg_file, new_config = load_configuration_handle_errors(
            #         self.config_file
            #     )
            #     self.__init__(new_config, self.script.name, cfg_file)  # type: ignore
            #     # ignore above because if self.script was None program would've already quit in __init__
            #     self.executor.start()
            #     self.restart()

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
            exception(e)
        finally:
            os._exit(0)

    def start_server(self) -> None:
        """
        Starts the server. All reloading and stuff is done here.
        """
        log("stella", "starting stella")
        log(
            "stella",
            f"using config file located at `{self.config_file}`",
        )
        browser_text = f"and listening at `{self.url}` on the browser"
        log(
            "stella",
            f"executing `{self.executor.command_to_display if self.script else ''}` {browser_text if self.RELOAD_BROWSER else ''}",
        )
        browser_text = ", `rb` to refresh browser page"
        log(
            "stella",
            f"input `rs` to manually restart the server{browser_text if self.RELOAD_BROWSER else ''} & `ex` to stop the server",
        )
        input_thread = Thread(target=self.manual_input)
        input_thread.start()
        self.executor.start()
        self.restart()
