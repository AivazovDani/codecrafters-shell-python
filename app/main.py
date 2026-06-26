import sys
import os
import shutil
import subprocess
import shlex # splitting '', "", /, _ and spaces. Everything
import readline # library that adds arrow keys up down like a real shell and remembers history of commands

import re

# Programmic Completions
completers = {}

# Handeling TAB completion for build in commands and PATH executables
builtins = ['echo', 'exit', 'type', 'cd', 'pwd', 'complete', 'jobs', 'history', 'declare']

# Background Jobs List | Jobs
jobs = []


# We declare it once at the start / refresh of the shell | History
written_commands = 0

# Declaire Variables | Declare
declares = {}



class AutoCompleter:
    def __init__(self, completers, builtins):
        self.completers = completers
        self.builtins = builtins

    def completer(self, text, state):

        options = []

        line = readline.get_line_buffer() # user command from buffer
        words = line.split() # split it into parts

        # If user is typing args | Check 1

        if ' ' in line and len(words) >= 1 and words[0] in self.completers:
            
            completer_path = self.completers[words[0]] # get the path for the command from completers dict
            
            env = os.environ.copy() # copy of all the enviroment variables (as a dict) into env
            
            env['COMP_LINE'] = line # set a new key, value
            
            env['COMP_POINT'] = str(len(line)) # same
            
            
            result = subprocess.run(
                [completer_path, words[0], text, words[-2] if len(words) > 2 else words[0]], # by default subprocess accepts 3 args
                capture_output=True,
                text=True,
                env=env
            )

            options = [match + ' ' for match in result.stdout.splitlines()]

            # "push\npull\n".splitlines() => ["push", "pull"]
            # ["push " , "pull "] after adding trailing space

            return options[state] if options else None
        
        # User is typing command | Check 2

        elif len(words) <= 1: # if there is no space == user has typed/typing a command
            
            options += [cmd + ' ' for cmd in self.builtins if cmd.startswith(text)]
            
            if len(options) == 0: # if the command is not built in, we need to check if it's a PATH executable

                for directory in os.environ.get('PATH', '').split(":"):

                    if os.path.exists(directory):
                        
                        options += [f + ' ' for f in os.listdir(directory) if f.startswith(text)] # checking for all the PATH executables that match our stdin
                    
                options = sorted(options) # sorting alfabetically | worst case O(log n)
        
        else: # args not in completers dict

            word = line.split()[-1] # get the args only
            
            parts = word.rsplit("/", 1) # split them by /
            
            if len(parts) > 1 and os.path.isdir(parts[0]):
                path = parts[0]
                prefix = parts[1]

            else:

                path = "."
                prefix = word

            options = [f + ' ' for f in os.listdir(path) if f.startswith(prefix)]


        if len(options) == 1 and state == 0: # if there is only 1 executable match
            return options[0] if state == 0 else None

            

        return options[state] if state < len(options) else None

    def display_matches(self, substitution, options, longest_match_len): # this is build in readline but i override it to fit my case
        sys.stdout.write("\n")
        sys.stdout.write("  ".join(options))
        sys.stdout.write("\n$ " + readline.get_line_buffer())
        sys.stdout.flush()

    def setup(self):
        readline.set_completer(self.completer) # register your tab completion function
        readline.parse_and_bind("tab: complete") # bind tab key to completion
        readline.set_completion_display_matches_hook(self.display_matches) # runs when there are more than one match to show
        readline.set_auto_history(True) # It tells readline to automatically add every command typed with input() to the history.


def run_builtins(command):
    global written_commands # remembers every built in command from the current session


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
            
            parts = command.split()

            if len(parts) > 1 and parts[1] == '-r':
                path = parts[2]

                if os.path.exists(path):
                    with open(path, 'r') as f:
                        for line in f:
                            readline.add_history(line.strip())

            elif len(parts) > 1 and parts[1] == '-w':
                path = parts[2]

                with open(path, 'w') as f:
                    for i in range(1, readline.get_current_history_length() + 1):
                        f.write(readline.get_history_item(i) + '\n')


            elif len(parts) > 1 and parts[1] == '-a':
                
                path = parts[2]
                current_length = readline.get_current_history_length() # update the written_command to the current lenght of the all commands in history (current session)
                readline.append_history_file(current_length - written_commands, path)
                written_commands = current_length # update the global variable

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

        elif command.startswith('declare'):
            parts = command.split()

            if len(parts) == 2:
                variables = parts[1].split('=')
                pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'

                if re.match(pattern, variables[0]):
                    variable_name = variables[0]

                    variable_value = variables[1]

                    declares[variable_name] = variable_value

                else:
                    return f"declare: `{parts[1]}': not a valid identifier"

            elif parts[1] == '-p':
                variable_name = parts[2]

                if variable_name not in declares.keys():
                    return f'declare: {parts[2]}: not found'
                else:
                    return f'declare -- {parts[2]}="{declares[parts[2]]}"'
        

def setup_history():
    # Sets the history file path 

    histfile = os.environ.get("HISTFILE") or os.path.expanduser("~/.shell_history")

    try:

        readline.read_history_file(histfile) # tries to load previous sessions history commands so i can use the arrow up key
        
    except (OSError, FileNotFoundError):
        pass # file doesn't exist yet that's fine

    return histfile



# Check for running jobs before the shell starts
def check_background_jobs():
    output = ""

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

            output += f'[{i+1}]{marker}  {'Done':<24}{original}' + '\n'
            jobs[i] = None
    
    return output


def replace_variable_name(command):
    # Replace variable name with the real value
    for name, value in declares.items():
        command = command.replace(f'${{{name}}}', value)
        command = command.replace(f'${name}', value)

    command = re.sub(r'\$\{?\w+\}?', '', command)  # remove any remaining $vars


    return command


def pipelines(command):
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



def run_tasks_in_background(command):
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

        return f'[{len(jobs)}] {process.pid}'
    else:
        return f'{cmd}: command not found'



def main():


    # History Commands
    HISTFILE = setup_history()

    # Auto Complete
    completer = AutoCompleter(builtins, completers)
    completer.setup()

    # REPL (read the command, parse and evaluate (execute) it, display the output, return to step 1)
    while True:
        
        # Check for background jobs
        result = check_background_jobs()
        if result:
            print(result, end='')

        command = input("$ ")

        # Replace variables $NAME, {} in command
        command = replace_variable_name(command)


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
            pipelines(command)


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

        elif command.startswith('declare'):
            result = run_builtins(command)
            print(result) if result != None else ''

        # Run tasks in the background
        elif command.endswith('&'):
            result = run_tasks_in_background(command)
            print(result)

        else:
            parts = shlex.split(command)
            cmd = parts[0]
            args = parts[1:]
            
            path = shutil.which(cmd)
            if path:
                subprocess.run([cmd] + args) # finds the command (bin/cat) and executes it with the arguments (main.py) | subprocess
            else:
                print(f'{cmd}: command not found')

    readline.write_history_file(HISTFILE) # write commands from the previous history file to HISTFILE



if __name__ == "__main__":
    main()