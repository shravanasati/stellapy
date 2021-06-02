import os

def walk() -> list[str]:
    """
    The `walk` function recursively searches for all files in the project returns a list of
    valid files.
    """
    # TODO check for gitignore files
    try:
        project_files = []
        for (root,_,files) in os.walk('.', topdown=True):
            if ".git" in root:
                continue
            for file in files:
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
        print(get_file_content(i))
        print("---------------------------------------------")
        _ = input()