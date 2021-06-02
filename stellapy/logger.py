from datetime import datetime

def log(severity:str, message:str) -> None:
    time = datetime.now().strftime("%d-%m-%y %H:%M:%S")
    color_red = "\033[31m"
    color_green = "\033[32m"
    color_blue = "\033[36m"
    color_reset = "\033[0m"

    if severity == "stella":
        print(f"{color_blue}[stella] {time} -> {message} {color_reset}")

    elif severity == "info":
        print(f"{color_green}[stella] {time} -> {message} {color_reset}")

    elif severity == "error":
        print(f"{color_red}[stella] {time} -> {message} {color_reset}")

    else:
        print("FATAL ERROR: This should never happen. You might want to open an issue on GitHub.")
        quit(1)