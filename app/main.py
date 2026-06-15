import sys
import os
import shutil

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

            if command == 'echo' or command == 'exit':
                print(f'{command} is a shell builtin')

            else:

                if shutil.which(command) and os.access(command, os.X_OK):
                    print(f'{command} is {os.path.abspath(command)}')

                else:
                    print(f'{command}: not found')

        else:
            print(f'{command}: command not found')


if __name__ == "__main__":
    main()
