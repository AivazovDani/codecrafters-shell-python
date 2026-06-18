import sys
import os
import shutil
import subprocess
import shlex # splitting '', "", /, _ and spaces. Everything
import readline # library that adds arrow keys up down like a real shell and remembers history of commands

import glob


# Handeling TAB completion for build in commands and PATH executables | HARD
builtins = ['echo', 'exit', 'type', 'cd', 'pwd']

def completer(text, state): # built in eadline but overriding it to fit my case
            line = readline.get_line_buffer()
            words = line.split()
            options = []
            # check builtins

            if len(words) <= 1: # if there is no space measn the user has typed a command not args to a command for autocomplete
                # readline.get_line_buffer() return the full current line the user has typed, cause the command variable is set in our main function and this is outside it
                options += [cmd + ' ' for cmd in builtins if cmd.startswith(text)]

                # here the state means how many times we pressed the tab. Each time we press the tab we cycle throught the commands in our options. Readlines update the state every time like: tab 1 = state=0 ; tab 2 = state=1. So the state it becomes index we can use to get the options in our list
                
                if len(options) == 0: # if we don\t have any PATH executable in our list with commands
                    # checking for executables in each directory in PATH (directories in linux where executable programs are stored)

                    for directory in os.environ.get('PATH', '').split(":"):
                        if os.path.exists(directory):
                            options += [f + ' ' for f in os.listdir(directory) if f.startswith(text)] # checking for all the commands that match our stdin
                        
                    options = sorted(options) # sorting alfabetically | worst case O(log n)
            
            else:
                word = readline.get_line_buffer().split()[-1]
                parts = word.rsplit("/", 1)
                
                if len(parts) > 1 and os.path.isdir(parts[0]):
                    path = parts[0]
                    prefix = parts[1]
                else:
                    path = "."
                    prefix = word
    
                options = [f + ' ' for f in os.listdir(path) if f.startswith(prefix)]


            if len(options) == 1 and state == 0: # if there is only 1 executable match
                return options[0]

                return None # tell readline there are no more commands

            return options[state] if state < len(options) else None


def display_matches(substitution, options, longest_match_len): # this is build in readline but i override it to fit my case
    print()
    print("  ".join(sorted(options)))

    sys.stdout.write("$ " + readline.get_line_buffer())
    sys.stdout.flush()

readline.set_completer(completer) # register your tab completion function
readline.parse_and_bind("tab: complete") # bind tab key to completion
readline.set_completion_display_matches_hook(display_matches) # runs when there are more than one match to show


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



