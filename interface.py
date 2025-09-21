# file: interface.py
import os
try:
    # For Unix-like systems
    import readline
except ImportError:
    # For Windows
    import pyreadline3 as readline

from main import execute_command

COMMANDS = ["ls", "cd", "pwd", "mkdir", "rm", "monitor", "exit"]


def completer(text, state):
    """Autocomplete for commands and file/directory names."""
    buffer = readline.get_line_buffer().strip().split()
    
    # Suggest commands if the buffer is empty or it's the first word
    if not buffer or len(buffer) == 1 and not readline.get_line_buffer().endswith(' '):
        options = [cmd for cmd in COMMANDS if cmd.startswith(text)]
    # Suggest files/dirs if it's the second word
    else:
        try:
            files = os.listdir(".")
            options = [f for f in files if f.startswith(text)]
        except Exception:
            options = []

    if state < len(options):
        return options[state]
    return None


def start_cli():
    """Initializes and runs the command-line interface loop."""
    readline.set_completer_delims(" \t\n;")
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)

    print("Simple Python Shell. Type 'exit' to quit.")
    while True:
        try:
            command = input(">> ")
            if command.strip().lower() == "exit":
                break
            
            if command.strip():
                readline.add_history(command)
                output = execute_command(command)
                if output:
                    print(output)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            print("\nExiting...")
            break

# Main execution block to run the CLI
if __name__ == "__main__":
    start_cli()