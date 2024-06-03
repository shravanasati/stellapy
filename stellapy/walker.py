from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Iterable

import gitignorefile
from watchdog.events import (
    EVENT_TYPE_CLOSED,
    EVENT_TYPE_OPENED,
    FileSystemEvent,
    FileSystemEventHandler,
)


def get_ignore_include_patterns(include_only: Iterable[str] | None):
    # todo use stella.ignore and .gitignore together
    ignore_filepath = find_ignore_file()
    ignore_match = (
        gitignorefile.parse(ignore_filepath) if ignore_filepath else lambda _: False
    )
    include_match = (
        gitignorefile._IgnoreRules(
            [gitignorefile._rule_from_pattern(pattern) for pattern in include_only],
            ".",
        ).match
        if include_only
        else lambda _: True
    )

    return ignore_match, include_match


class GitignoreMatchingEventHandler(FileSystemEventHandler):
    """
    Subclass of `watchdog.FileSystemEventHandler` which implements gitignore-style
    pattern matching.
    """

    def __init__(
        self,
        include_only: Iterable[str] | None,
        poll_interval: float,
        callback: Callable[[], None],
    ) -> None:
        super().__init__()
        self.ignore_match, self.include_match = get_ignore_include_patterns(
            include_only
        )
        self.poll_interval = poll_interval
        self.callback_fn = callback
        self.last_event_time = datetime.now()

    def on_any_event(self, event: FileSystemEvent) -> None:
        # only respond to events after a certain threshold
        if datetime.now() - self.last_event_time > timedelta(
            milliseconds=self.poll_interval
        ):
            super().on_any_event(event)
            self.callback_fn()
            self.last_event_time = datetime.now()

    def dispatch(self, event: FileSystemEvent) -> None:
        no_dispatch_conditions = {
            self.ignore_match(event.src_path),
            ".git" in event.src_path,
            event.event_type in (EVENT_TYPE_OPENED, EVENT_TYPE_CLOSED),
            not self.include_match(event.src_path),
        }
        if any(no_dispatch_conditions):
            return
        return super().dispatch(event)


def find_ignore_file(base_dir: str | None = None) -> str | None:
    """
    Recursively tries to find the `stella.ignore` in current directory and its parents until it's found,
    if not, reverts to `.gitignore`.
    """
    stella_ignore_file = __find_file_recursively("stella.ignore", base_dir)
    if stella_ignore_file:
        return stella_ignore_file
    else:
        return __find_file_recursively(".gitignore", base_dir)


def find_config_file(base_dir: str | None = None) -> str | None:
    """
    Recursively tries to find the `stella.yml` config file in current directory and its parents until
    it's found.
    """
    return __find_file_recursively("stella.yml", base_dir)


def __find_file_recursively(filename: str, base_dir: str | None = None) -> str | None:
    """
    Tries to find `filename` in `base_dir` and its parents until it's found.
    """
    cwd = Path("./").absolute() if not base_dir else Path(base_dir)
    # if this is the root directory, its parent is also same, so stop checking
    if cwd.parent == cwd:
        return None
    try:
        _ = open(cwd / filename)
        return str(cwd / filename)
    except (FileNotFoundError,):
        return __find_file_recursively(filename, str(cwd.parent))


if __name__ == "__main__":
    print(find_ignore_file())
    print(find_config_file())
    input()
    # for i in walk(["*.py"], False):
    #     ...
    #     print(i)
    #     input()
    #     print(get_file_content(i))
    #     input()
