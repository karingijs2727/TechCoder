import openai
import re
import time
import os
import copy




openai.api_key = ''
model_id = 'gpt-3.5-turbo-16k'
temp = 0.3 # NOW 0.7 RUNNING



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




class TechCoder():
    def __init__(self):
        self.load_json_roles = []
        with open("config/python/roles.json", "r") as f:
            print(f.read())



TC = TechCoder()
























































































