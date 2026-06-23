import sys
import os
import shutil
import subprocess
import shlex # splitting '', "", /, _ and spaces. Everything
import readline # library that adds arrow keys up down like a real shell and remembers history of commands

# Programmic Completions
completers = {}

# Handeling TAB completion for build in commands and PATH executables | HARD
builtins = ['echo', 'exit', 'type', 'cd', 'pwd', 'complete', 'jobs', 'history']

# Background Jobs List
jobs = []


def completer(text, state): # built in eadline but overriding it to fit my case

            line = readline.get_line_buffer() # get's the command the user typed from the buffer
            words = line.split() # split it into parts to determine if there are 2 or less. If less the user is still typing a command not an args
            options = []
            # check builtins

            # checks for command then space and searches in completers for the command and suggest commands
            if ' ' in line and len(words) >= 1 and words[0] in completers:
                completer_path = completers[words[0]] # get the path for the command in completers
                
                env = os.environ.copy() # copy of all the enviroment variables as a dict into env
                env['COMP_LINE'] = line # set a new key, value
                env['COMP_POINT'] = str(len(line))
                
                
                result = subprocess.run(
                    [completer_path, words[0], text, words[-2] if len(words) > 2 else words[0]], # by default subprocess accept 3 args
                    capture_output=True,
                    text=True,
                    env=env
                )
                options = [line + ' ' for line in result.stdout.splitlines()]
                # "push\npull\n".splitlines() > ["push", "pull"]
                # ["push " , "pull "] after adding trailing space
                return options[state] if options else None
            


            if len(words) <= 1: # if there is no space means the user has typed a command not args to a command for autocomplete
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
                word = readline.get_line_buffer().split()[-1] # get the args only
                parts = word.rsplit("/", 1) # split them by /
                
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
    sys.stdout.write("\n")
    sys.stdout.write("  ".join(options))
    sys.stdout.write("\n$ " + readline.get_line_buffer())
    sys.stdout.flush()

readline.set_completer(completer) # register your tab completion function
readline.parse_and_bind("tab: complete") # bind tab key to completion
readline.set_completion_display_matches_hook(display_matches) # runs when there are more than one match to show
readline.set_auto_history(True) # It tells readline to automatically add every command typed with input() to the history.

def run_builtins(command):
    

    if command.split()[0] in builtins:
                        
        if command.startswith('echo'):
            parts = shlex.split(command)
            return " ".join(parts[1:])

        elif command == 'exit':

            return 'exit'
        
        elif command.startswith('cd'):
            parts = command.split()
            cmd = parts[0]
            absolute_path = parts[1]

            if os.path.exists(absolute_path): # check if the file or directory exists. Works for relative, absolute paths of directories and files
                os.chdir(absolute_path) # change current directory to the new one
            
            elif absolute_path == '~':
                os.chdir(os.path.expanduser(absolute_path)) # expand ~ to /home/yordan-ayvazov

            else:
                return f'cd: {absolute_path}: No such file or directory'

        elif command.startswith('type'):
            command = command.replace('type ','')


            if command in builtins:
                return f'{command} is a shell builtin'

            else:

                if shutil.which(command): # checks if the file exists even outside my disk and the access status | shutil.which(cat)
                    return f'{command} is {shutil.which(command)}'

                else:
                    return f'{command}: not found'


        elif command.startswith('pwd'):
            
            return os.getcwd() # get the absolute path of the current directory to standout

        elif command.startswith('complete'):
            parts = command.split()
        
            flag = parts[1]

            if flag == '-p':
                cmd = parts[2]

                if cmd in completers:
                    return f"complete -C '{completers[cmd]}' {cmd}"
                else:
                    return f'complete: {cmd}: no completion specification'
            
            elif flag == '-C':
                path = parts[2]
                cmd = parts[3]

                completers[cmd] = path
            
            elif flag == '-r':
                cmd = parts[2]

                if cmd in completers:
                    del completers[cmd]
                else:
                    return f'complete: {cmd}: no completion specification'

        elif command == 'jobs':
            not_none_indices = [i for i in range(len(jobs)) if jobs[i] is not None]

            output = ""

            for i in range(len(jobs)):
                if jobs[i] == None:
                    continue

                process, original = jobs[i]

                status = 'Running' if process.poll() is None else 'Done'
                suffix = ' &' if process.poll() is None else ''
                
                if i == not_none_indices[-1]:      # highest job number
                    marker = '+'
                elif i == not_none_indices[-2]:    # second highest job number
                    marker = '-'
                else:
                    marker = ' '
                
                output += f'[{i+1}]{marker}  {status:<24}{original}{suffix}' + '\n'
                        
            for i in range(len(jobs)):
                if jobs[i] == None:
                    continue
                
                process, original = jobs[i]
                
                if process.poll() is not None:
                    jobs[i] = None
            
            
            return output

        elif command.startswith('history'):
            written_commands = 0
            parts = command.split()

            if len(parts) > 1 and parts[1] == '-r':
                path = parts[2]

                if os.path.exists(path):
                    with open(path, 'r') as f:
                        for line in f:
                            readline.add_history(line.strip())

            elif len(parts) > 1 and parts[1] == '-w':
                path = parts[2]

                if os.path.exists(path):
                    with open(path, 'w') as f:
                        for i in range(1, readline.get_current_history_length() + 1):
                            f.write(readline.get_history_item(i) + '\n')
                            written_commands += 1


            elif len(parts) > 1 and parts[1] == '-a':
                global written_commands
                path = parts[2]
                current_length = readline.get_current_history_length()
                readline.append_history_file(current_length - written_commands, path)
                written_commands = current_length

            else:

                command = parts[0]
                number = int(parts[1]) if len(parts) > 1 else None

                lenght = readline.get_current_history_length()
                output = ""

                if number is not None:
                    for i in range(lenght - number + 1, lenght + 1):
                        output += f'{i:>4}  {readline.get_history_item(i)}\n'

                else:
                    for i in range(1, lenght + 1):
                        output += f'{i:>4}  {readline.get_history_item(i)}\n'

                return output

                

                
def main():
    # REPL (read the command, parse and evaluate (execute) it, display the output, return to step 1)
    while True:
        
        # Check for running jobs before the shell starts
        for i in range(len(jobs)):
            if jobs[i] == None:
                continue
            
            process, original = jobs[i]

            if process.poll() is not None:
                not_none_indicess = [i for i in range(len(jobs)) if jobs[i] is not None]
                
                if i == not_none_indicess[-1] or len(not_none_indicess) == 1: # highest job number
                    marker = '+'
                elif i == not_none_indicess[-2]: # second highest job number
                    marker = '-'
                else:
                    marker = ' '

                print(f'[{i+1}]{marker}  {'Done':<24}{original}')
                jobs[i] = None

        command = input("$ ")
        

        if command == 'exit':
            
            result = run_builtins(command)
            if result == 'exit':
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

        # Pipelines
        elif '|' in command:
            parts = command.split('|')

            first_command = parts[0]

            if first_command.split()[0] in builtins:
                result = run_builtins(first_command)
                
                
                if result is not None:
                    result = result.encode() + b'\n'

                    for i in range(1, len(parts)):

                        if (len(parts) - 1) == i:
                            if parts[i].split()[0] not in builtins:
                                p = subprocess.Popen(shlex.split(parts[i].strip()), stdin=subprocess.PIPE)
                                p.communicate(input=result)
                            else:
                                command = parts[i].strip()
                                print(run_builtins(command))

                        
                        else:
                            if isinstance(result, bytes):
                                p = subprocess.Popen(shlex.split(parts[i].strip()), stdin=subprocess.PIPE)
                                p.communicate(input=result)
                            else:
                                result = subprocess.Popen(shlex.split(parts[i].strip()), stdin=result.stdout, stdout=subprocess.PIPE)


            else:

                for i in range(len(parts)):

                    if i == 0:
                        result = subprocess.Popen(shlex.split(parts[i].strip()), stdout=subprocess.PIPE)
                    
                    elif (len(parts) - 1) == i:
                        if parts[i].split()[0] not in builtins:
                            result = subprocess.Popen(shlex.split(parts[i].strip()), stdin=result.stdout)
                            result.communicate()
                        else:
                            command = parts[i].strip()
                            print(run_builtins(command))

                    
                    else:
                        result = subprocess.Popen(shlex.split(parts[i].strip()), stdin=result.stdout, stdout=subprocess.PIPE)




        elif command.startswith('pwd'):
            result = run_builtins(command)
            print(result)

        elif command.startswith('cd'):
            result = run_builtins(command)
            print(result) if result != None else ''
                
        elif command.startswith("echo"):
            result = run_builtins(command)
            print(result)

        elif command.startswith("type"):
            result = run_builtins(command)
            print(result)


        elif command.startswith('complete'):
            result = run_builtins(command)
            print(result) if result != None else ''
            
        elif command == 'jobs':
            result = run_builtins(command)
            print(result, end='')

        elif command.startswith('history'):
            result = run_builtins(command)
            print(result, end='') if result != None else ''

        # Run tasks in the background
        elif command.endswith('&'):
            command = command.rstrip('&').strip()
            parts = shlex.split(command)
            cmd = parts[0]
            args = parts[1:]
            
            path = shutil.which(cmd) # finds full path of executable in PATH and checks for executable permissions
            if path:
                process = subprocess.Popen([path] + args) # starts a process and returns immediately without waiting for it to finish:
                
                slot_found = False
                for i in range(len(jobs)):

                    if jobs[i] == None:
                        slot_found = True
                        break
                
                if slot_found:
                    jobs[i] = (process, command)
                else:
                    jobs.append((process, command))

                print(f'[{len(jobs)}] {process.pid}')
            else:
                print(f'{cmd}: command not found')

                

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

