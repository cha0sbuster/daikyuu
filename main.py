import sys
import os

import discord
import dotenv

from bot.bot import Bot
from client.completion import CompletionClient


class LLMBot(discord.Client):
    def __init__(self, file_path: str, completion_client: CompletionClient):
        self.bot = Bot(file_path, completion_client)

        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents=intents)

    async def on_ready(self):
        # TODO: enable pfp switching too
        # with open(pfp_path, 'rb') as profile_img:
        #   await client.user.edit(username=self.bot.name, avatar=profile_img.read()) 

        if self.user.name != self.bot.name:
            await client.user.edit(username=self.bot.name) 

        print(f'Logged in as {self.user} (ID: {self.user.id})')

    async def on_message(self, message: discord.Message): 
        if type(message.channel) != discord.channel.DMChannel:
            return

        if message.author.id == self.user.id:
            return

        async with message.channel.typing():
            res = self.bot.resolve_chat(message.author.name, message.author.global_name, message.content)
            await message.channel.send(res)


if __name__ == '__main__':
    dotenv.load_dotenv()

    if len(sys.argv) < 2:
        print("please pass character json file")
        exit()

    completion_client = CompletionClient(os.getenv('COMPLETIONS_MODEL', 'gpt-4'), os.getenv('OPEN_AI_BASE_URL'))
    client = LLMBot(sys.argv[1], completion_client)
    client.run(os.getenv('DISCORD_KEY', ''))
