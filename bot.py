import os
import discord
import yaml
from discord.ext import commands
from discord_components import DiscordComponents, ComponentsBot

#print(discord.__version__)  # check to make sure at least once you're on the right version!


class AlwaysOnDude(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='.',
                        intents=discord.Intents.all(),
                        help_command=commands.MinimalHelpCommand(),
                        chunk_guilds_at_startup=True,
                        )
        self.discord_components = DiscordComponents(self)                
        self.to_load = [
            "cogs.BasicCommands",
            "cogs.economy",
            "cogs.games",
            "cogs.myevents"
        ]

        for cog in self.to_load:
            self.load_cog(cog)
        
            
    def load_cog(self, cog: str):
        try:
            self.load_extension(cog)
            print(f"Loded extension {cog}")
        except Exception as e:
            print(e)



'''
client = commands.Bot(command_prefix='.', intents=intents, chunk_guilds_at_startup=True)



for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
        print(f"Loded extension cogs.{filename[:-3]}")        
'''

with open(r'data/token.yaml') as file:
    token = yaml.load(file, Loader=yaml.FullLoader)

client = AlwaysOnDude()
client.run(token['TOKEN'])  # recall my token was saved!