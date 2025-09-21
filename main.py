# file: main.py
from commands import (
    list_files,
    change_directory,
    print_working_directory,
    make_directory,
    remove_path,
)
from system_monitor import system_status


def execute_command(command: str) -> str:
    """Parses and executes a given command string."""
    parts = command.strip().split()
    if not parts:
        return ""
    cmd, *args = parts

    if cmd == "ls":
        return list_files()
    elif cmd == "cd" and args:
        return change_directory(args[0])
    elif cmd == "pwd":
        return print_working_directory()
    elif cmd == "mkdir" and args:
        return make_directory(args[0])
    elif cmd == "rm" and args:
        return remove_path(args[0])
    elif cmd == "monitor":
        return system_status()
    else:
        return f"Error: Unsupported or invalid command '{cmd}'"