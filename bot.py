import os
import discord
from discord.ext import commands

#print(discord.__version__)  # check to make sure at least once you're on the right version!

token = open("token.txt", "r").read()  # I've opted to just save my token to a text file. 

#intents = discord.Intents.all()
#client = discord.Client(intents=intents)

client = commands.Bot(command_prefix='.')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
        print(f"Loded extension cogs.{filename[:-3]}")        






client.run(token)  # recall my token was saved!