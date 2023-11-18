import os
from gitignore_parser import parse_gitignore
from pathlib import Path


def walk() -> list:
    """
    The `walk` function recursively searches for all files in the project returns a list of
    valid files.
    """
    gitignore_file_path = find_gitignore()
    ignore_match = (
        parse_gitignore(gitignore_file_path, "./")
        if gitignore_file_path
        else lambda _: False
    )

    try:
        # project_files = []
        for root, _, files in os.walk(".", topdown=True):
            # todo ignore match not working
            if ".git" in root or ignore_match(root):
                continue

            for file in files:
                yield os.path.join(root, file)
                # project_files.append(os.path.join(root, file))

        # return project_files

    except Exception as e:
        print(e)
        return []


def get_file_content(filepath: str) -> str:
    """
    `get_file_content` returns the content of the file.
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            fc = f.read()

        return fc

    except Exception as e:
        print(e)
        return ""


def find_gitignore(base_dir: str | None = None) -> str | None:
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
        return cwd / filename
    except (FileNotFoundError,):
        return __find_file_recursively(filename, cwd.parent)


if __name__ == "__main__":
    print(find_gitignore())
    print(find_config_file())
    input()
    for i in walk():
        ...
        print(i)
        # input()
        # print(get_file_content(i))
        # input()
