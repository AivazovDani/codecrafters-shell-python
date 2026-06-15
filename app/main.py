import sys


def main():
    # REPL (read the command, parse and evaluate (execute) it, display the output, return to step 1)
    while True:
        sys.stdout.write("$ ")
        command = input()
        if command == 'exit':
            break
        elif command.startswith("echo"):
            print(command.replace("echo", "").split())
        else:
            print(f'{command}: command not found')


if __name__ == "__main__":
    main()
