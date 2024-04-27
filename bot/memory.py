import json
from typing import List, Dict
import dataclasses
import datetime

from bot.dialog import Dialog, ChatEntry


DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# TODO: handle this better, this is horrible lol

def load_memory(bot_name: str) -> Dict[str, Dialog]:
    dialogs = {}
    try:
        with open(f'./memory/{bot_name}.json', 'r') as memory_file:
            memory_data = json.load(memory_file)
            for username, raw_dialog in memory_data['dialogs'].items():
                dialogs[username] = Dialog()
                entries = []
                for entry in raw_dialog:
                    entry['time'] = datetime.datetime.strptime(entry['time'], DATETIME_FORMAT)
                    entries.append(entry)
                dialogs[username].log = [ChatEntry(**entry) for entry in entries]
    except FileNotFoundError:
        pass
    return dialogs

def save_memory(bot_name: str, dialogs: Dict[str, Dialog]) -> None:
    to_dump: Dict = {'dialogs': {}}
    with open(f'./memory/{bot_name}.json', 'w+') as memory_file:
        for username, dialog in dialogs.items():
            raw_entries = []
            for entry in dialog.log:
                raw_entry = dataclasses.asdict(entry)
                raw_entry['time'] = raw_entry['time'].strftime(DATETIME_FORMAT)
                raw_entries.append(raw_entry)
            to_dump['dialogs'][username] = raw_entries
        json.dump(to_dump, memory_file)
