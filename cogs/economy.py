import discord
import logging
import math
import database
import pprint as debug
from datetime import datetime
from discord.ext import commands

class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.db = database.Database()

    @commands.command()
    async def points(self, ctx):
        async with ctx.message.channel.typing():
            self.db.connect()
            points = self.db.getPoints(ctx.guild.name, ctx.author.id)
            self.db.close_connection()
            await ctx.send(f"{ctx.author.mention} has {points} points")
            
def setup(client):
    client.add_cog(Economy(client))
