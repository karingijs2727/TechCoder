import openai
import re
import time
import os
import copy
import json



with open("key.txt", "r") as f:
    openai.api_key = f.read()

model_id = 'gpt-3.5-turbo-16k'
temp = 0.1 # NOW 0.7 RUNNING

std = "Make sure there is one Main file. And make sure to use com.technik.plugin; package."

#task = "Make a Minecraft plugin in java. The plugin should include 2 commands /home and /sethome"
task = """Make a command /enderchest that will open 1 rows gui with name "enderchest menu" and in each slot enderchest item with slot id in name if player click the enderchest then the gui will close and new will open with 6 rows and name "enderchest <id of last clicked slot>" Player is able to put items and take items from this gui and items from gui willl be saved to yaml for each player individual each enderchest will have own id in yaml. """

task = f"{std}. {task}"

def ChatGPT_conversation(conversation, temps):
    if temps == 0:
        response = openai.ChatCompletion.create(
            model=model_id,
            messages=conversation,
            temperature=temp
        )
        conversation.append({'role': response.choices[0].message.role, 'content': response.choices[0].message.content})
    else:
        response = openai.ChatCompletion.create(
            model=model_id,
            messages=conversation,
            temperature=temps
        )
        conversation.append({'role': response.choices[0].message.role, 'content': response.choices[0].message.content})
    return conversation


def send_api(text, temps=None):
    conversation = []
    conversation.append({'role': 'system', 'content': f'{text}'})
    conversation = ChatGPT_conversation(conversation, temps)
    return conversation[-1]['content'].strip()

def print_lines_update(file_names, codes_list, file_names2, codes_list2):
    file2 = []
    codes2 = []
    print(file_names)
    print(file_names2)

    for x in range(len(file_names2)):
        if file_names2[x] not in file_names:
            print(f"File: {file_names2[x]}")
            for line in codes_list2[x].split("\n"):
                print("+ " + line)

    for x in range(len(file_names)):
        if file_names[x] in file_names2:
            idx = file_names2.index(f"{file_names[x]}")
            file2 = file_names2[idx]
            codes2 = codes_list2[idx]
            print("YESSSSSSSSSSSSS....")
        else:
            #print("continue")
            continue
        added_lines, removed_lines = find_added_and_removed_lines(codes_list[x], codes2)
        print(f"File: {file2}")
        print("Added lines:")
        for line in added_lines:
            print("+ " + line)
        print("\nRemoved lines:")
        for line in removed_lines:
            print("- " + line)


def extract_java_code_and_filenames(text):
    text = f" {text}"
    select_counter = 1
    full_str = ""

    codes_list = []
    files_list = []

    for i in range(len(text) - 1, -1, -1):
        full_str = f"{text[i]}{full_str}"
        if select_counter == 1:
            if "```" in full_str:
                select_counter += 1
                full_str = ""
        if select_counter == 2:
            if "```" in full_str:
                full_str = full_str.replace("```", "")
                codes_list.insert(0, full_str)
                select_counter += 1
                full_str = ""
        if select_counter == 3:
            if "```" in full_str:
                select_counter = 2
                full_str = ""
                continue
            if "yml" in full_str:
                ##select_counter = 1
                full_str = "yml"
                select_counter += 1
            if "java" in full_str:
                full_str = "java"
                select_counter += 1
            if "json" in full_str:
                full_str = "json"
                select_counter += 1
            if "hson" in full_str:
                full_str = "hson"
                select_counter += 1
            #if "class" in full_str:
            #    full_str = "class"
            #    select_counter += 1
            if "h2" in full_str:
                full_str = "h2"
                select_counter += 1
            if "sqlite" in full_str:
                full_str = "sqlite"
                select_counter += 1
            if "xml" in full_str:
                full_str = "xml"
                select_counter += 1
            if "md" in full_str:
                full_str = "md"
                select_counter += 1
        if select_counter == 4:
            if " " in full_str or "\n" in full_str or "`" in full_str or "*" in full_str or '"' in full_str or "<" in full_str or "/" in full_str:
                file_namey = full_str
                if "`" in full_str:
                    full_str = "`"
                    file_namey = file_namey[1:]
                else:
                    file_namey = file_namey[1:]
                select_counter = 1
                # print(">>>" + full_str + "<<<")
                file_namey = file_namey.replace('"', "")
                file_namey = file_namey.replace("*", "")
                file_namey = file_namey.replace("**", "")
                file_namey = file_namey.replace("<", "")
                #if "." not in full_str:
                #    pass
                files_list.insert(0, file_namey)

    full_code_str = ""
    for java_code, file_name in zip(codes_list, files_list):
        full_code_str += file_name
        full_code_str += "\n\n```"
        full_code_str += java_code
        full_code_str += "```\n\n"

    print(files_list)

    return files_list, codes_list, full_code_str

import difflib


def find_added_and_removed_lines(code1, code2):
    lines1 = code1.splitlines()
    lines2 = code2.splitlines()

    differ = difflib.Differ()
    diff = list(differ.compare(lines1, lines2))

    added_lines = [line[2:] for line in diff if line.startswith('+ ')]
    removed_lines = [line[2:] for line in diff if line.startswith('- ')]

    return added_lines, removed_lines

class ManagerHumman():
    def __init__(self):
        self.type = "1"  # 1. create or 2. continue
        self.codes = []
        self.names = []
        self.human_prompts = []
        self.file = "code"
        self.error = ""
        self.skip = 0
        self.features = []
        self.feature_desc = []
        self.issues = []

    def make_full_str(self):

        # print("=================================================")
        # for x in range(len(self.names)):
        #    print(f"{self.names[x]}\n\n```{self.codes[x]}\n```")
        #    print("=================================================")

        full_str = ""
        for x in range(len(self.names)):
            full_str += f"{self.names[x]}\n\n```{self.codes[x]}\n```"
        return full_str

    def save_human_prmots(self):
        full_str = ""
        print("SAVE HUMAN")
        print(self.human_prompts)
        print(full_str)
        for x in range(len(self.human_prompts)):
            if len(self.human_prompts[x]) != 0:
                full_str += f"{self.human_prompts[x]}\n"
        try:
            with open(f"{self.file}/human_prompts.txt", "w") as f:
                f.write(full_str)
        except:
            with open(f"{self.file}/human_prompts.txt", "a") as f:
                f.write(full_str)
        print(full_str)
        print("SAVE HUMAN")

    def save_files(self, file_names, codes_list, file_names2, codes_list2):
        selected_file_names = []
        selected_file_codes = []

        for x in range(len(file_names2)):
            if "java" == file_names2[x]:
                print("JAVA_ERROR<<<")
                print("JAVA_ERROR<<<")
                continue
            selected_file_names.append(file_names2[x])
            selected_file_codes.append(codes_list2[x])
            print(file_names2[x] + " A")
        for x in range(len(file_names)):
            if file_names[x] not in file_names2:
                print(file_names[x] + " B")
                selected_file_names.append(file_names[x])
                selected_file_codes.append(codes_list[x])
        print("-----------------------")
        print(file_names)
        print(file_names2)

        for x in range(len(selected_file_names)):
            try:
                with open(f"{self.file}/{selected_file_names[x]}", "w") as f:
                    f.write(selected_file_codes[x])
            except:
                with open(f"{self.file}/{selected_file_names[x]}", "a") as f:
                    f.write(selected_file_codes[x])
        try:
            with open(f"{self.file}/task.txt", "w") as f:
                f.write(task)
        except:
            with open(f"{self.file}/task.txt", "a") as f:
                f.write(task)
        print("Done files saved")

    def organize_files_set_to_last(self, file_names, codes_list, file_names2, codes_list2):
        self.codes = []
        self.names = []
        for x in range(len(file_names2)):
            self.names.append(file_names2[x])
            self.codes.append(codes_list2[x])
        for x in range(len(file_names)):
            if file_names[x] not in file_names2:
                self.names.append(file_names[x])
                self.codes.append(codes_list[x])
        while True:
            try:
                idx = self.names.index("java")
                self.names.pop(idx)
            except:
                try:
                    os.remove(f"{self.file}/java")
                except: pass
                break



MH = ManagerHumman()


class TechCoder():
    def __init__(self):
        self.load_json_roles = []
        self.plugin_panner = []
        self.programmer = []
        self.error_fixer = []
        self.helper = []
        self.roles_data = []
        #with open("config/python/roles.json", "r") as f:
        #    print(f.read())
        with open("config/plugins3/roles.json", "r") as f:
            self.roles_data = json.load(f)
        self.plugin_panner = self.roles_data['Plugin Planner']
        self.plugin_panner = "\n".join(self.plugin_panner)
        self.programmer = self.roles_data["Programmer"]
        self.programmer = "\n".join(self.programmer)

        self.helper = self.roles_data["Helper"]
        self.helper = "\n".join(self.helper)
        self.error_fixer = self.roles_data["Error Fixer"]
        self.error_fixer = "\n".join(self.error_fixer)

        self.msg_2 = """Code:
<CODE>

Agnet 1: <AGENT1>
Agent 2: <AGENT2>

Make it a long conversation to talk about every detail.
Every agent should talk at least once think critical and come up with good solutions. And make sure at the end of conversation to end up with Features: <text>.
There is one rule in conversation don't write any code.
Hold a conversation between agent 1 and 2 when the conversation is finished end conversation with a Features so respond with format Features: <text>.
<EXTRA_INFO>
Make sure to use this respond format:
Agent <nr>: <text>
Features: <text>"""

        self.msg_3 = """Code:
<CODE>

Agnet 1: <AGENT1>
Agent 2: <AGENT2>
Agent 3: <AGENT3>

Make it a long conversation to talk about every detail.
Every agent should talk at least once think critical and come up with good solutions. And make sure at the end of conversation to end up with Features: <text>.
There is one rule in conversation don't write any code.
Hold a conversation between agent 1 and 2 and 3 when the conversation is finished end conversation with a Features so respond with format Features: <text>.
<EXTRA_INFO>
Make sure to use this respond format:
Agent <nr>: <text>
Features: <text>"""

        self.msg_4 = """Code:
<CODE>

Agnet 1: <AGENT1>
Agent 2: <AGENT2>
Agent 3: <AGENT3>
Agent 4: <AGENT4>

Make it a long conversation to talk about every detail.
Every agent should talk at least once think critical and come up with good solutions. And make sure at the end of conversation to end up with Features: <text>.
There is one rule in conversation don't write any code.
Hold a conversation between agent 1 and 2 and 3 and 4 when the conversation is finished end conversation with a Features so respond with format Features: <text>.
<EXTRA_INFO>
Make sure to use this respond format:
Agent <nr>: <text>
Features: <text>"""

        self.msg = """Code:
<CODE>

Instructions:
<INSTRUCTIONS>

You are a programmer youre task is to implement things from Instructions to the code update only code blocks that need a change implement all comments to the code.
Implement everything from Instructions to the code don't skip any thing.

Respond format:
file: <FULL_FILENAME>

```<CODE HERE>```"""

        self.conv_summary = """<CONV>


<NEW_TASK>
"""

SELECT = 0
PROJECT_NAME = "test"

while True:
    print("Select 1 to start new project")
    print("Select 2 to continue project")
    choice = input("Select: ")
    if choice == "1":
        SELECT = "1"
        name = input("Project Name: ")
        MH.file = name
        if os.path.exists(f"{name}") == False:
            os.mkdir(f"{name}")
            break
        else:
            time.sleep(999999999999999999999999999999999999999)
        break
    if choice == "2":
        name = input("Project Name: ")
        MH.file = name
        PROJECT_NAME = name
        if os.path.exists(f"{name}") == True:
            pass
        else:
            time.sleep(999999999999999999999999999999999999999)

        for file in os.listdir(MH.file):
            if "java" in file.lower():
                with open(f"{MH.file}/{file}") as f:
                    MH.names.append(file)
                    MH.codes.append(f.read())
        try:
            with open(f"{MH.file}/human_prompts.txt", "r") as f:
                lines = f.readlines()
            for line in lines:
                if len(line) > 2:
                    MH.human_prompts.append(line)
        except:
            pass
        try:
            with open(f"{self.file}/task.txt", "a") as f:
                task = f.read()
            print("--------------(Task)--------------")
            print(task)
            print("--------------(Task)--------------")
        except:
            pass
        break



TC = TechCoder()


if SELECT == "1":
    msg = TC.msg_4
    msg = msg.replace("<AGENT1>", TC.plugin_panner)
    msg = msg.replace("<AGENT2>", TC.programmer)
    msg = msg.replace("<AGENT3>", TC.helper)
    msg = msg.replace("<AGENT4>", TC.error_fixer)
    msg = msg.replace("{task}", task)
    msg = msg.replace("<EXTRA_INFO>", 'Make sure to respond with format Features: <text> Force to continue and make a summary of features to implement from the conversation only the things that need to be implemented to the code dont skip any thing do it step by step and respond with every detail.')

    print(msg)
    output = send_api(msg, 0.85)
    print(output)

    msg = TC.conv_summary
    msg = msg.replace("<CONV>", output)
    msg = msg.replace("<NEW_TASK>", "")

    try:
        instructions = output.split("Features")[2]
    except:
        instructions = output.split("Features")[1]
    if "\n\n" in instructions:
        instructions = instructions.split("\n\n")[0]
    instructions = instructions[1:]

    msg = TC.msg
    msg = msg.replace("<INSTRUCTIONS>", instructions)
    print(msg)
    output = send_api(msg, 0.15)
    print(output)

    file_names, codes_list, full_code_str = extract_java_code_and_filenames(output)
    MH.names = file_names
    MH.codes = codes_list
    MH.save_files(MH.names, MH.codes, file_names, codes_list)
    MH.skip = 1

choice = "0"

#task = "Add a system to have more than 1 home."

FINISHED_STATUS = False

#Make sure to close the gui from enderchest menu when player click on a slot

while True:
    print("(1). Pass")
    print("(2). Select runs.")
    print("(3). New Task")
    if MH.skip <= 0:
        choice = input("Choice: ")

    if choice == "3":
        task = input("Task: ")
        choice = "1"
    if choice == "2":
        MH.skip = int(input("Runs: "))
        choice = "0"
    if choice == "1" or MH.skip > 0:

        print(f"RUNS ({MH.skip}) <<<<<<<<<<<<<<<<<<<<<")
        print(f"RUNS ({MH.skip}) <<<<<<<<<<<<<<<<<<<<<")
        print(f"RUNS ({MH.skip}) <<<<<<<<<<<<<<<<<<<<<")

        msg = TC.msg_4
        msg = msg.replace("<CODE>", MH.make_full_str())
        msg = msg.replace("<AGENT1>", TC.plugin_panner)
        msg = msg.replace("<AGENT2>", TC.programmer)
        msg = msg.replace("<AGENT3>", TC.helper)
        msg = msg.replace("<AGENT4>", TC.error_fixer)
        msg = msg.replace("{task}", task)
        #msg = msg.replace("<EXTRA_INFO>", "After <INFO> make a summary of the features from the conversation that can be used explain them step by step how to implement them write only the ones that are not implemented to the code.")
        #msg = msg.replace("<EXTRA_INFO>", "After <INFO> make a summary of the features that are missing in the code and need to be implemented you know it from the conversation that can be used explain them step by step how to implement them write only the ones that are not implemented to the code. Explain it in details so programmer will know what to do. If everything is implemented respond with FINISHED2.")
        #msg = msg.replace("<EXTRA_INFO>", "After <INFO> make a summary of the features that are missing in the code and need to be implemented to the code. You know it from the conversation. Explain it step by step how to implement them write only the ones that are not implemented to the code. Explain it in details so programmer will know what to do. If everything is implemented respond with FINISHED2.")
        msg = msg.replace("<EXTRA_INFO>", 'Make sure to respond with format Features: <text> Force to continue and make a summary of features to implement from the conversation only the things that need to be implemented to the code dont skip any thing do it step by step and respond with every detail.')
        print("-------------------------(SEND-(1))-------------------------")
        print(msg)
        print("-------------------------(RECV-(1))-------------------------")
        output = send_api(msg, 0.85)
        print(output)

        try:
            instructions = output.split("Features")[2]
        except:
            instructions = output.split("Features")[1]
        if "\n\n" in instructions:
            instructions = instructions.split("\n\n")[0]
        instructions = instructions[1:]
        if "FINISHED2" in output:
            FINISHED_STATUS = True

        msg = TC.msg
        msg = msg.replace("<INSTRUCTIONS>", instructions)
        msg = msg.replace("<CODE>", MH.make_full_str())
        print("-------------------------(SEND-(2))-------------------------")
        print(msg)
        print("-------------------------(RECV-(2))-------------------------")
        output = send_api(msg, 0.15)
        print(output)

        file_names2, codes_list2, full_code_str = extract_java_code_and_filenames(output)

        print_lines_update(MH.names, MH.codes, file_names2, codes_list2)
        MH.organize_files_set_to_last(MH.names, MH.codes, file_names2, codes_list2)
        MH.save_files(MH.names, MH.codes, file_names2, codes_list2)

        if FINISHED_STATUS == True:
            print("The plugin is finished.")
            time.sleep(99999999999999999999999999999999999)

    MH.skip -= 1


































































