import sys
import os
import shutil
import subprocess

def main():
    # REPL (read the command, parse and evaluate (execute) it, display the output, return to step 1)
    while True:
        sys.stdout.write("$ ")
        command = input()
        

        if command == 'exit':
            break

        elif command.startswith('pwd'):

            print(os.getcwd()) # get the absolute path of the current directory to standout

        elif command.startswith('cd'):
            parts = command.split()
            cmd = parts[0]
            absolute_path = parts[1]

            if os.path.exists(absolute_path): # check if the file or directory exists. Works for relative, absolute paths of directories and files
                os.chdir(absolute_path) # change current directory to the new one
            
            elif absolute_path == '~':
                os.chdir(os.path.expanduser(absolute_path)) # expand ~ to /home/yordan-ayvazov

            else:
                print(f'cd: {absolute_path}: No such file or directory')
                
        elif command.startswith("echo"):
            statment = command[5:].strip()
            print(statment)

        elif command.startswith("type"):
            command = command.replace('type ','')

            if command == 'echo' or command == 'exit' or command == 'type' or command == 'pwd':
                print(f'{command} is a shell builtin')

            else:

                if shutil.which(command): # checks if the file exists even outside my disk and the access status | shutil.which(cat)
                    print(f'{command} is {shutil.which(command)}')

                else:
                    print(f'{command}: not found')

        else:
            parts = command.split()
            cmd = parts[0]
            args = parts[1:]
            
            path = shutil.which(cmd)
            if path:
                subprocess.run([cmd] + args) # finds the command (bin/cat) and executes it with the arguments (main.py) | subprocess
            else:
                print(f'{cmd}: command not found')


if __name__ == "__main__":
    main()
