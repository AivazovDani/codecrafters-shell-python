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
                    path = command.split(" ")
                    args = path[1:]
                    command = path[:1]
                    subprocess.run([command] + args)
                    
                else:
                    print(f'{command}: not found')

        else:
            print(f'{command}: command not found')


if __name__ == "__main__":
    main()
