import os
from logging import exception
from pathlib import Path
from typing import Iterable

import gitignorefile

IGNORE_PATTERN = None
INCLUDE_PATTERN = None


def get_ignore_include_patterns(include_only: Iterable[str] | None):
    global IGNORE_PATTERN, INCLUDE_PATTERN
    if IGNORE_PATTERN and INCLUDE_PATTERN:
        # if they are already cached
        return IGNORE_PATTERN, INCLUDE_PATTERN

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

    # compute patterns once and cache them
    IGNORE_PATTERN = ignore_match
    INCLUDE_PATTERN = include_match
    return IGNORE_PATTERN, INCLUDE_PATTERN


def walk(include_only: Iterable[str] | None, follow_symlinks: bool):
    """
    The `walk` function recursively searches for all files in the project returns a list of
    valid files.
    """

    try:
        ignore_match, include_match = get_ignore_include_patterns(include_only)
        # project_files = []
        for root, _, files in os.walk(".", topdown=True, followlinks=follow_symlinks):
            if ".git" in root or ignore_match(root):
                continue

            for file in files:
                if ignore_match(root):
                    continue
                if include_match(file):
                    yield os.path.join(root, file)
                # project_files.append(os.path.join(root, file))

        # return project_files

    except Exception as e:
        exception(e)
        return []


def get_file_content(filepath: str) -> str:
    """
    `get_file_content` returns the content of the file. Ignores binary files.
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            fc = f.read()

        return fc

    except UnicodeDecodeError:
        # binary file, ignore
        return ""

    except Exception as e:
        exception(e)
        return ""


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
    for i in walk(["*.py"], False):
        ...
        print(i)
        # input()
        # print(get_file_content(i))
        # input()
