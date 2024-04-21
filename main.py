import sys
import os

import discord
import dotenv

import bot


class LLMBot(discord.Client):
    def __init__(self, file_path):
        self.bot = bot.Bot(file_path)

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

    async def on_message(self, message): 
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

    client = LLMBot(sys.argv[1])
    client.run(os.getenv('DISCORD_KEY'))
