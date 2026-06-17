import sys
import os
import shutil
import subprocess
import shlex # splitting '', "", /, _ and spaces. Everything
import readline # library that adds arrow keys up down like a real shell and remembers history of commands

# Handeling TAB completion for build in commands and PATH executables
builtins = ['echo', 'exit', 'type', 'cd', 'pwd']
autocomplete = builtins.copy()

# checking for executables in each directory in PATH (directories in linux where executable programs are stored)
for directory in os.environ.get('PATH', '').split(":"):
    if os.path.exists(directory)
    dir_list = os.listdir(directory)
    autocomplete += dir_list

def completer(text, state):
            # all commands the user would type
            options = []

            # check builtins
            options += [cmd + ' ' for cmd in autocomplete if cmd.startswith(text)]
            
            # here the state means how many times we pressed the tab. Each time we press the tab we cycle throught the commands in our options. Readlines update the state every time like: tab 1 = state=0 ; tab 2 = state=1. So the state it becomes index we can use to get the options in our list
            if state < len(options):
                return options[state]
            return None


readline.set_completer(completer) # register your tab completion function
readline.parse_and_bind("tab: complete") # bind tab key to completion


def main():
    # REPL (read the command, parse and evaluate (execute) it, display the output, return to step 1)
    while True:
        sys.stdout.write("$ ")
        command = input()
        

        if command == 'exit':
            break

        elif '2>>' in command:
            parts = command.split("2>>")

            file = parts[1]

            command_parts = shlex.split(parts[0])

            with open(file.strip(), 'a') as f:
                subprocess.run(command_parts, stderr=f)

        elif '>>' in command or '1>>' in command:
            command = command.replace("1>>", ">>")
            parts = command.split(">>")

            file = parts[1]

            command_parts = shlex.split(parts[0])

            with open(file.strip(), 'a') as f:
                subprocess.run(command_parts, stdout=f)
        
        elif '2>' in command:

            parts = command.split("2>")
            file = parts[1]

            command_parts = shlex.split(parts[0])

            with open(file.strip(), 'w') as f:
                subprocess.run(command_parts, stderr=f)

        elif '>' in command or '1>' in command:
            command = command.replace("1>", ">")

            parts = command.split(">")

            file = parts[1]

            command_parts = shlex.split(parts[0])
            

            with open(file.strip(), 'w') as f:
                subprocess.run(command_parts, stdout=f)

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
            parts = shlex.split(command)
            print(" ".join(parts[1:]))

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
            parts = shlex.split(command)
            cmd = parts[0]
            args = parts[1:]
            
            path = shutil.which(cmd)
            if path:
                subprocess.run([cmd] + args) # finds the command (bin/cat) and executes it with the arguments (main.py) | subprocess
            else:
                print(f'{cmd}: command not found')

if __name__ == "__main__":
    main()


