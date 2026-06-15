import sys
import os


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
            command = command.replace('type ','')

            if command.startswith('echo') or command.startswith('exit'):
                print(f'{command} is a shell builtin')

            else:

                if os.path.exists(command) and os.access(path, os.X_OK):
                    print(os.path.abspath(command))

                else:
                    print(f'{command}: not found')

        else:
            print(f'{command}: command not found')


if __name__ == "__main__":
    main()
