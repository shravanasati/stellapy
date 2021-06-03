import os
import igittigitt

def _is_ignored(file:str) -> bool:
    try:
        parser = igittigitt.IgnoreParser()
        parser._parse_rule_file("./.gitignore")
        return parser.match(file)

    except Exception as e:
        print(e)

def walk() -> list:
    """
    The `walk` function recursively searches for all files in the project returns a list of
    valid files.
    """
    try:
        project_files = []
        for (root,_,files) in os.walk('.', topdown=True):
            if ".git" in root:
                continue

            for file in files:
                if not _is_ignored(file): 
                    project_files.append(os.path.join(root, file))
                # print(os.path.exists(os.path.join(root, file)))

        return project_files

    except Exception as e:
        print(e)

def get_file_content(filepath:str) -> str:
    """
    `get_file_content` returns the content of the file.
    """
    try:
        with open(filepath) as f:
            fc = f.read()

        return fc

    except Exception as e:
        print(e)

if __name__ == "__main__":
    for i in walk():
        print(i)
        input()
        print(get_file_content(i))
        input()