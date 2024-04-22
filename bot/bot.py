import os
import json
import datetime
from typing import List, Dict
from dataclasses import dataclass

import openai
import httpx

from bot.dialog import Dialog
from client.completion import CompletionClient, BASE_TOKENS, PER_MESSAGE_TOKENS


class Bot:
    def __init__(self, file_path: str, client: CompletionClient) -> None:
        with open(file_path, 'r') as bot_file:
            bot_data = json.load(bot_file)
        
        self.name: str = bot_data.get('name', 'Assistant')
        self.personality: str = bot_data.get('personality', 'A helpful assistant')

        self.client = client

        self.dialogs: Dict[str, Dialog] = {} # map username -> Dialog objects
    
    def resolve_chat(self, username: str, user_nick: str, user_text: str) -> str:
        if username not in self.dialogs:
            self.dialogs[username] = Dialog()
        dialog = self.dialogs[username] 

        dialog.append_user_chat(user_text, self.client.get_token_length(user_text) + PER_MESSAGE_TOKENS)
        bot_text = self.client.get_completion(self.get_messages(dialog, user_nick))
        dialog.append_bot_chat(bot_text, self.client.get_token_length(bot_text) + PER_MESSAGE_TOKENS)
        return bot_text

    def get_messages(self, dialog: Dialog, user_nick: str) -> List[Dict[str, str]]:
        messages = [
            {'role': 'system', 'content': f"Write {self.name}'s next reply in a fictional chat between {self.name} and {user_nick}. Write 1 reply only in internet RP style, avoid quotation marks. Be proactive, creative, and drive the plot and conversation forward. Always stay in character and avoid repetition. The chat is taking place on Discord in a direct message."},
            {'role': 'system', 'content': f"{self.name} is {user_nick}'s Discord friend. The setting is the real world, no magical or fantasy elements."},
            {'role': 'system', 'content': f"{self.name}'s personality: {self.personality}"},
            {'role': 'system', 'content': 'Always stay in character.'},
        ]

        # first time vs recent chat system messages
        # TODO: condition on memories existing instead of log length
        if len(dialog.log) < 2:
            messages.append({'role': 'system', 'content': f"This is the first time {self.name} and {user_nick} have ever spoken. Introduce yourself and try to learn more about {user_nick}."})
        else:
            last_message_delta = datetime.datetime.now() - dialog.log[-2].time
            mins_ago = last_message_delta.seconds / 60.0
            messages.append({'role': 'system', 'content': f"The last time {self.name} and {user_nick} spoke was {mins_ago} minutes ago"})
        
        current_token_count = BASE_TOKENS + sum([self.client.get_token_length(msg['content']) for msg in messages]) + PER_MESSAGE_TOKENS
        messages += dialog.get_truncated_messages(self.client.max_tokens - current_token_count)
        return messages