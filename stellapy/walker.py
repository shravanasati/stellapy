import os

def walk() -> list:
    """
    The `walk` function recursively searches for all files in the project returns a list of
    valid files.
    """
    supported_ext = {"html", "css", "js", "py", "rb", "go", "rs", "php", "java"}
    try:
        project_files = []
        for (root,_,files) in os.walk('.', topdown=True):
            if ".git" in root:
                continue

            for file in files:
                ext = file.split('.')[-1]
                if ext in supported_ext:
                    project_files.append(os.path.join(root, file))

        return project_files

    except Exception as e:
        print(e)
        return []

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
        return ""

# if __name__ == "__main__":
#     for i in walk():
#         print(i)
#         input()
#         print(get_file_content(i))
#         input()