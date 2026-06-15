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

            if command == 'echo' or command == 'exit' or command == 'type':
                print(f'{command} is a shell builtin')

            else:

                if shutil.which(command): # checks if the file exists even outside my disk and the access status
                    print(f'{command} is {shutil.which(command)}')

                else:
                    print(f'{command}: not found')

        elif shutil.which(command):
            args = command.split(" ")[1:]
            subprocess.run([path] + args)

        else:
            print(f'{command}: command not found')


if __name__ == "__main__":
    main()
