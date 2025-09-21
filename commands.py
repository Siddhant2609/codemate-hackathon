# file: commands.py
import os
import shutil


def list_files() -> str:
    try:
        return "\n".join(os.listdir()) or "[empty directory]"
    except Exception as e:
        return f"Error: {e}"


def change_directory(path: str) -> str:
    try:
        os.chdir(path)
        return f"Changed directory to {os.getcwd()}"
    except FileNotFoundError:
        return f"Error: Directory '{path}' not found"
    except NotADirectoryError:
        return f"Error: '{path}' is not a directory"
    except Exception as e:
        return f"Error: {e}"


def print_working_directory() -> str:
    return os.getcwd()


def make_directory(path: str) -> str:
    try:
        os.mkdir(path)
        return f"Directory '{path}' created"
    except FileExistsError:
        return f"Error: Directory '{path}' already exists"
    except Exception as e:
        return f"Error: {e}"


def remove_path(path: str) -> str:
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return f"Removed '{path}'"
    except FileNotFoundError:
        return f"Error: '{path}' not found"
    except Exception as e:
        return f"Error: {e}"
