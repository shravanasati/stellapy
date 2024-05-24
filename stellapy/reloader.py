from dataclasses import dataclass
from datetime import datetime, timedelta
from logging import exception
from threading import Lock, Thread
from time import sleep
from typing import Any, Callable, Generic, TypeVar

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from watchdog.observers import Observer

from stellapy.configuration import Configuration, load_configuration_handle_errors
from stellapy.executor import Executor
from stellapy.logger import log
from stellapy.walker import GitignoreMatchingEventHandler

T = TypeVar("T")
ActionFunc = Callable[["Trigger"], None]
ErrorHandlerFunc = Callable[["Trigger", Exception], None]


@dataclass(frozen=True)
class Trigger(Generic[T]):
    """
    Similar to contexts in go, a trigger carries an action to perform at a certain datetime, along with an error handler and a value.
    """

    action: ActionFunc
    when: datetime
    error_handler: ErrorHandlerFunc | None
    value: T

    def __repr__(self) -> str:
        return f"Trigger <action={self.action} when={self.when} error_handler={self.error_handler} value={self.value}>"


class TriggerQueue:
    """
    A list of triggers offering some useful and thread-safe methods.
    The type variable `T` is used for the value of Trigger.
    """

    def __init__(self) -> None:
        self.triggers: list[Trigger[Any]] = []
        self.__lock = Lock()

    def add(self, trigger: Trigger[Any]):
        """
        Add a trigger to the queue.
        """
        with self.__lock:
            self.triggers.append(trigger)

    def execute_remaining(self):
        """
        Executes all the triggers that need to be executed, i.e., whose deadline has been reached.
        """
        now = datetime.now()
        with self.__lock:
            # store all ready triggers in a temp list
            to_execute = [t for t in self.triggers if now >= t.when]
            self.triggers = [t for t in self.triggers if t not in to_execute]

        for trigger in to_execute:
            try:
                trigger.action(trigger)
            except Exception as e:
                if trigger.error_handler:
                    trigger.error_handler(trigger, e)
                else:
                    raise e

    def cancel_all(self):
        """
        Cancel all the scheduled triggers.
        """
        with self.__lock:
            self.triggers.clear()


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

        # watchdog observer
        self.observer = Observer()
        self.observer.schedule(
            GitignoreMatchingEventHandler(
                self.config.include_only, self.config.poll_interval, self._restart
            ),
            ".",
            recursive=True,
        )

        # trigger executor
        self._finished = False  # used by trigger thread to look for exits
        self.trigger_execution_interval = 0.1  # seconds
        self.trigger_queue = TriggerQueue()
        self.trigger_thread = Thread(target=self._trigger_executor)
        self.trigger_thread.start()

        # convert to seconds
        self.poll_interval = self.config.poll_interval / 1000
        self.browser_wait_delta = timedelta(
            milliseconds=self.config.browser_wait_interval
        )

    def _trigger_executor(self):
        """
        Executes all the remaining triggers in the trigger queue until `self._finished`
        is set to `True`.
        """
        while not self._finished:
            self.trigger_queue.execute_remaining()
            sleep(self.trigger_execution_interval)

    def _start_browser(self):
        # selenium driver
        if self.config.browser not in ("firefox", "chrome", "safari", "edge"):
            # this should never happen because of configuration validation
            raise Exception(f"invalid browser={self.config.browser}")

        match self.config.browser.lower():
            case "firefox":
                self.driver = webdriver.Firefox()
            case "chrome":
                self.driver = webdriver.Chrome()
            case "safari":
                self.driver = webdriver.Safari()
            case "edge":
                self.driver = webdriver.Edge()
            case _:
                raise Exception(f"unknown browser={self.config.browser}")

        try:
            self.driver.get(self.url)

        except Exception as e:
            se = str(e)
            if "Message: unknown error: cannot find Chrome binary" in se:
                log(
                    "error",
                    "chrome binary not found. either install chrome browser or configure stella browser to firefox.",
                )
                self.stop()

            elif "net::ERR_" in se or "Reached error page" in se:
                log(
                    "error",
                    f"browser startup failed, retrying in {self._displayable_seconds_from_timedelta(self.browser_wait_delta)} seconds",
                )
                self.trigger_queue.add(
                    Trigger(
                        action=self._browser_reloader,
                        when=datetime.now() + self.browser_wait_delta,
                        error_handler=self._browser_reload_error_handler,
                        value=self.browser_wait_delta,
                    )
                )

            else:
                log("error", f"an unknown error occurred: \n{e}")
                self.stop()

    def _browser_reloader(self, _: Trigger[timedelta]):
        """
        A helper function used in browser reload triggers.
        """
        self.driver.refresh()
        # firefox throws an error via selenium if the refresh wasn't successfull
        # chrome and edge don't, so we can't call the error handler function (exponential backoff)
        # even if the page wasn't loaded
        # thus, check if the body tag has `neterror` class because it's always present
        # when any browser(again, not tested for safari) shows the error page
        # not sure how safari behaves, so we'll check for it too
        if self.config.browser != "firefox":
            try:
                el = self.driver.find_element(By.CLASS_NAME, "neterror")
            except NoSuchElementException:
                return
            else:
                if el.tag_name == "body":
                    raise Exception("failed to load page")

    @staticmethod
    def _displayable_seconds_from_timedelta(t: timedelta):
        """
        Helper function to return seconds from a timedelta object, because if t.seconds < 1,
        then t.seconds is zero for a timedelta object.
        """
        if t.seconds > 0:
            return t.seconds
        else:
            return (t.microseconds) / 10e6

    def _browser_reload_error_handler(self, t: Trigger[timedelta], e: Exception):
        log(
            "error",
            f"browser reload didnt work, retrying in {self._displayable_seconds_from_timedelta(2*t.value)} seconds...",
        )
        self.trigger_queue.add(
            Trigger(
                action=t.action,
                when=datetime.now() + 2 * t.value,
                error_handler=self._browser_reload_error_handler,
                value=2 * t.value,
            )
        )

    def _restart(self):
        log(
            "info",
            "detected changes in the project, reloading server and browser",
        )
        # cancel all prev triggers, because we got a new change
        self.trigger_queue.cancel_all()
        self.executor.re_execute()
        if self.RELOAD_BROWSER:
            self.trigger_queue.add(
                Trigger[timedelta](
                    action=self._browser_reloader,
                    when=datetime.now() + self.browser_wait_delta,
                    error_handler=self._browser_reload_error_handler,
                    value=self.browser_wait_delta,
                ),
            )

    def manual_input(self) -> None:
        """
        Manual restart and exit.
        """
        while not self._finished:
            try:
                message = input().lower().strip()
            except EOFError:
                break

            if message == "ex":
                log("info", "stopping server")
                self.stop()

            elif message == "rs":
                log("info", "restarting the server")
                self.trigger_queue.cancel_all()
                self.executor.re_execute()
                if self.RELOAD_BROWSER:
                    self.trigger_queue.add(
                        Trigger(
                            action=self._browser_reloader,
                            when=datetime.now() + self.browser_wait_delta,
                            error_handler=self._browser_reload_error_handler,
                            value=self.browser_wait_delta,
                        )
                    )

            elif message == "rb":
                if self.RELOAD_BROWSER:
                    try:
                        log("info", "trying to reload browser window")
                        self.driver.refresh()
                    except Exception:
                        log("error", "unable to refresh browser window")
                else:
                    log(
                        "stella",
                        "no browser URL is configured, can't refresh browser window",
                    )

            elif message == "rc":
                log(
                    "stella",
                    "attempting to reload configuration, stopping existing commands and browser windows",
                )
                self.stop()
                cfg_file, new_config = load_configuration_handle_errors(
                    self.config_file
                )
                self.__init__(new_config, self.script.name, cfg_file)  # type: ignore
                # ignore above because if self.script was None program would've already quit in __init__
                self.start()

    def stop(self):
        try:
            self.trigger_queue.cancel_all()
            self.executor.close()
            if self.RELOAD_BROWSER:
                if getattr(self, "driver", "!nope!") != "!nope!":
                    # condition to check if driver was initialized
                    self.driver.quit()
        except Exception as e:
            log(
                "error",
                "an error occured while stopping the server, this should never happen.",
            )
            exception(e)
        finally:
            self._finished = True
            if self.observer.is_alive():
                self.observer.stop()
                self.observer.join()

    def start(self) -> None:
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
        # running the input thread as daemon would allow the program
        #  to exit even if the input thread is still running
        input_thread = Thread(target=self.manual_input, daemon=True)
        input_thread.start()
        self.executor.start()
        if self.RELOAD_BROWSER:
            self._start_browser()

        self.observer.start()
        # self.restart()
