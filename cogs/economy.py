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
        await ctx.send(f":bank: {ctx.author.mention} has **{points}** points :moneybag:")

    @commands.command()
    async def give(self, ctx, member, points):
        async with ctx.message.channel.typing():
            if member is None:
                await ctx.channel.send(f":bank:: :no_entry: **You have to specify a memeber after the commands**")
            try:    
                payment = int(points)
            except ValueError:
                await ctx.channel.send(f":bank:: :no_entry: **The amount has to be an integer non negative number**")
                return
            if payment<1:
                await ctx.channel.send(f":bank:: :no_entry: **The amount has to be an integer non negative number**")
                return
            
            self.db.connect()
            sender_amount= self.db.getPoints(ctx.guild.name, ctx.author.id)
            self.db.close_connection()
            if sender_amount<payment:
                await ctx.channel.send(f":bank:: :x: **Insufficient amount**")
                return

            user = int(member.strip('<!@>'))
            member = await ctx.guild.fetch_member(user)

            self.db.connect()
            recipient_amount= self.db.getPoints(ctx.guild.name, member.id)
            self.db.setPoints(ctx.guild.name, ctx.author.id, sender_amount-payment) #decreace sender's points 
            self.db.setPoints(ctx.guild.name, member.id, recipient_amount+payment) #increase recipient's points
            self.db.close_connection()

            await ctx.channel.send(f":bank:: :white_check_mark: {ctx.author.mention} gave **{payment}** points:moneybag: to {member.mention}")



            
def setup(client):
    client.add_cog(Economy(client))
