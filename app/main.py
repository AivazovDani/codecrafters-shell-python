import sys


def main():
    # REPL (read the command, parse and evaluate (execute) it, display the output, return to step 1)
    while True:
        sys.stdout.write("$ ")
        command = input()
        # if command == 'exit':
        #     break
        # elif command.startswith("echo"):
        #     print(command.replace("echo ", ""))
        if command.startswith("echo", "exit", "type"):
            print(f'{command} is a shell builtin')
        else:
            print(f'{command}: not found')


if __name__ == "__main__":
    main()
