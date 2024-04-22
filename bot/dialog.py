import datetime
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class ChatEntry:
    role: str
    content: str
    time: datetime.datetime
    token_count: int

    def to_message(self) -> Dict[str, str]:
        return {'role': self.role, 'content': self.content}


class Dialog:
    def __init__(self) -> None:
        self.log: List[ChatEntry] = []

    def get_truncated_messages(self, max_tokens: int) -> List[Dict[str, str]]:
        used_tokens = 0
        res = []
        for entry in reversed(self.log):
            if used_tokens + entry.token_count > max_tokens:
                break
            used_tokens += entry.token_count
            res.append(entry.to_message())
        return list(reversed(res))

    def append_user_chat(self, user_text: str, token_count: int) -> None:
        self.log.append(ChatEntry('user', user_text, datetime.datetime.now(), token_count))

    def append_bot_chat(self, bot_text: str, token_count: int) -> None:
        self.log.append(ChatEntry('assistant', bot_text, datetime.datetime.now(), token_count))
