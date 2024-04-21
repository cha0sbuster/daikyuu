import os
import json

import openai


class Dialog:
    def __init__(self, username):
        self.username = username # globally unique, used to id this dialog, different from user_nick potentially
        self.rest_of_log = [] # historic messages, stored separately so the prefix is mutable (e.g. changing nicknames)

    def get_chat_log(self, bot_name, bot_personality, user_nick):
        return [
            {'role': 'system', 'content': f"Write {bot_name}'s next reply in a fictional chat between {bot_name} and {user_nick}. Write 1 reply only in internet RP style, avoid quotation marks. Be proactive, creative, and drive the plot and conversation forward. Always stay in character and avoid repetition. The chat is taking place on Discord."},
            {'role': 'system', 'content': f"{bot_name} is {user_nick}'s Discord friend. The setting is the real world."},
            {'role': 'system', 'content': f"[{bot_name}'s personality: {bot_personality}]"},
            *self.rest_of_log,
        ]

    def append_user_chat(self, user_text):
        self.rest_of_log.append({'role': 'user', 'content': user_text})
    
    def append_bot_chat(self, bot_text):
        self.rest_of_log.append({'role': 'assistant', 'content': bot_text})


class Bot:
    def __init__(self, file_path):
        with open(file_path, 'r') as bot_file:
            bot_data = json.load(bot_file)
        
        self.name = bot_data.get('name', 'Assistant')
        self.personality = bot_data.get('personality', 'A helpful assistant')

        self.model = os.getenv('COMPLETIONS_MODEL')
        self.client = openai.OpenAI(base_url=os.getenv('OPEN_AI_BASE_URL'))

        self.dialogs = {} # map username -> Dialog objects
    
    def resolve_chat(self, username, user_nick, user_text):
        if username not in self.dialogs:
            self.dialogs[username] = Dialog(username)
        dialog = self.dialogs[username] 

        dialog.append_user_chat(user_text)
        res = self.client.chat.completions.create(
            messages=dialog.get_chat_log(self.name, self.personality, user_nick),
            model=self.model,
            temperature=1.0,
            top_p=1.0,
            stop=['<|end_of_turn|>', '<|eot_id|>']
        )
        bot_text = res.choices[0].message.content
        dialog.append_bot_chat(bot_text)
        return bot_text
