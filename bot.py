import os
import discord
import yaml
from discord.ext import commands

#print(discord.__version__)  # check to make sure at least once you're on the right version!


#loads the bot token
with open(r'data/token.yaml') as file:
    token = yaml.load(file, Loader=yaml.FullLoader)

intents = discord.Intents.all()
#client = discord.Client(intents=intents)

client = commands.Bot(command_prefix='.', intents=intents, chunk_guilds_at_startup=True)


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
        print(f"Loded extension cogs.{filename[:-3]}")        


client.run(token['TOKEN'])  # recall my token was saved!