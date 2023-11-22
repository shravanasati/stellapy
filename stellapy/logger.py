from datetime import datetime

from rich import print
from rich.text import Text


def log(severity: str, message: str) -> None:
    """
    The `log` function logs the messages according to their severity.
    """
    current_time = datetime.now().strftime("%H:%M:%S")
    if severity == "stella":
        print(Text(f"[stella] {current_time} -> {message}", style="cyan"))

    elif severity == "info":
        print(Text(f"[stella] {current_time} -> {message}", style="green"))

    elif severity == "error":
        print(Text(f"[stella] {current_time} -> {message}", style="red"))

    else:
        print(
            "FATAL ERROR: Invalid value of the 'severity' parameter of log function. This should never happen. You might want to open an issue on GitHub."
        )
        quit(1)


if __name__ == "__main__":
    log("stella", "test1")
    log("info", "test2")
    log("error", "test3")
