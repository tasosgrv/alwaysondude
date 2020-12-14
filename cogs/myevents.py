import discord
import logging
import pprint as debug
from datetime import datetime
from discord.ext import commands


logging.basicConfig(filename='Alwaysondude.log', level=logging.INFO, filemode='w', format='%(asctime)s:%(name)s:%(message)s', datefmt='%d %b %y %H:%M:%S')

class MyEvents(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()  # event decorator/wrapper. More on decorators here: https://pythonprogramming.net/decorators-intermediate-python-tutorial/
    async def on_ready(self):  # method expected by client. This runs once when connected
        print(f'We have logged in as {self.client.user}')  # notification of login.

        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='my master to learn new things'))
    
        guild_id = self.client.guilds[0].id
        await self.client.fetch_guild(guild_id)
        
        for guild in self.client.guilds:
            debug.pprint(guild)
            for member in guild.members:
                debug.pprint(member)
                print("-"*30)
        '''
        for guild in self.client.guilds:
            for channel in guild.voice_channels:
                if channel.position == 3: 
                    await channel.connect()
        '''
    
    @commands.Cog.listener()
    async def on_message(self, message):  # event that happens per any message.
        # each message has a bunch of attributes. Here are a few.
        # check out more by print(dir(message)) for example.
        logging.info(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")
        print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")
        if message.author == self.client.user:
            return

        if "hello" in message.content.lower():
            await message.channel.send(f"Hello {message.author.mention}, i am your digital friend {self.client.user.mention}, Do not panic i am peaceful. Mr. w0ch4 is my master!")

        if  "fuck" in message.content.lower():
            await message.channel.send(f"Go to hell {message.author.mention}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"**:x: Command '{str(ctx.message.content).strip('.')}' is not found**")



def setup(client):
    client.add_cog(MyEvents(client))
