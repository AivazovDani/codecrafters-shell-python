import sys


def main():
    # REPL (read the command, parse and evaluate (execute) it, display the output, return to step 1)
    while True:
        sys.stdout.write("$ ")
        command = input()
        if command == 'exit':
            break
        elif command.startswith("echo"):
            print(command.replace("echo ", ""))
        elif command.startswith("type"):
            command.replace('type ','')
            if command.startswith('echo') or command.startswith('type') or command.startswith('exit'):
                print(f'{command} is a shell builtin')
            else:
                print(f'{command}: not found')
        else:
            print(f'{command}: command not found')


if __name__ == "__main__":
    main()
