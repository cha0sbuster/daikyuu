import os
import json
import datetime
from typing import List, Dict
from dataclasses import dataclass

import openai
import httpx


BASE_TOKENS = 1
PER_MESSAGE_TOKENS = 4
CONTEXT_LENGTH = 8000


@dataclass
class ChatEntry:
    role: str
    content: str
    time: datetime.datetime
    token_count: int


class Dialog:
    def __init__(self, username: str):
        self.username: str = username # globally unique, used to id this dialog, different from user_nick potentially
        self.rest_of_log: List[ChatEntry] = [] # historic messages, stored separately so the prefix is mutable (e.g. changing nicknames)

    def get_chat_log(self, bot, user_nick: str):
        # initial prompt
        log = [
            {'role': 'system', 'content': f"Write {bot.name}'s next reply in a fictional chat between {bot.name} and {user_nick}. Write 1 reply only in internet RP style, avoid quotation marks. Be proactive, creative, and drive the plot and conversation forward. Always stay in character and avoid repetition. The chat is taking place on Discord."},
            {'role': 'system', 'content': f"[{bot.name} is {user_nick}'s Discord friend. The setting is the real world, no magical or fantasy elements.]"},
            {'role': 'system', 'content': f"[{bot.name}'s personality: {bot.personality}]"},
            {'role': 'system', 'content': '[ALWAYS STAY IN CHARACTER]'},
        ]
        
        # first time vs recent chat system messages
        # TODO: condition on memories existing instead of log length
        if len(self.rest_of_log) < 2:
            log.append({'role': 'system', 'content': f"[This is the first time {bot.name} and {user_nick} have ever spoken.]"})
        else:
            last_message_delta = datetime.datetime.now() - self.rest_of_log[-2].time
            mins_ago = last_message_delta.seconds / 60.0
            log.append({'role': 'system', 'content': f"[The last time {bot.name} and {user_nick} spoke was {mins_ago} minutes ago]"})

        # only append the last N messages to fill up the context window, don't over over token limit
        # TODO: no need to recompute this every time... just here for flexibility
        current_token_count = BASE_TOKENS + sum([bot.token_length(msg['content']) for msg in log]) + PER_MESSAGE_TOKENS

        to_append = []
        for msg in reversed(self.rest_of_log):
            if current_token_count + msg.token_count + PER_MESSAGE_TOKENS > CONTEXT_LENGTH:
                break
            current_token_count += msg.token_count + PER_MESSAGE_TOKENS
            to_append.append({'role': msg.role, 'content': msg.content})
        log += reversed(to_append)

        return log

    def append_user_chat(self, user_text: str, token_count: int):
        self.rest_of_log.append(ChatEntry('user', user_text, datetime.datetime.now(), token_count))
    
    def append_bot_chat(self, bot_text: str, token_count: int):
        self.rest_of_log.append(ChatEntry('assistant', bot_text, datetime.datetime.now(), token_count))


class Bot:
    def __init__(self, file_path: str):
        with open(file_path, 'r') as bot_file:
            bot_data = json.load(bot_file)
        
        self.name: str = bot_data.get('name', 'Assistant')
        self.personality: str = bot_data.get('personality', 'A helpful assistant')

        self.model: str = os.getenv('COMPLETIONS_MODEL', 'gpt-4')
        self.client = openai.OpenAI(base_url=os.getenv('OPEN_AI_BASE_URL'))

        self.dialogs: Dict[str, Dialog] = {} # map username -> Dialog objects
    
    def resolve_chat(self, username: str, user_nick: str, user_text: str) -> str:
        if username not in self.dialogs:
            self.dialogs[username] = Dialog(username)
        dialog = self.dialogs[username] 

        dialog.append_user_chat(user_text,  self.token_length(user_text))
        res = self.client.chat.completions.create(
            messages=dialog.get_chat_log(self, user_nick),
            model=self.model,
            temperature=1.0,
            top_p=1.0,
            stop=['<|end_of_turn|>', '<|eot_id|>']
        )
        bot_text = res.choices[0].message.content or ''
        dialog.append_bot_chat(bot_text, self.token_length(bot_text))
        return bot_text

    # TODO: better abstraction for client so no circular dep between bot and dialog
    def token_length(self, text):
        tokens = self.client.post('/tokenize', cast_to=httpx.Response, body={"content": text})
        return len(tokens.json()['tokens'])