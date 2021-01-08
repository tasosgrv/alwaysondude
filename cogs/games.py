import discord
import math
import random
import re
import database
import games
import pprint as debug
from datetime import datetime
from discord.ext import tasks, commands

class Games(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.db = database.Database()

    
    @commands.command()
    async def coinflip(self, ctx, bet):
        try:    
            self.bet = int(bet)
        except ValueError:
            await ctx.channel.send(f":coin: : :no_entry: **The amount has to be an integer non-negative number**")
            return
        
        if self.bet<1:
            await ctx.channel.send(f":coin: : :no_entry: **The amount has to be an integer non-negative number**")
            return

        self.db.connect()
        points = self.db.getPoints(ctx.guild.name, ctx.author.id)
        self.db.close_connection()

        if self.bet>points:
            await ctx.channel.send(f":coin: : :x: **Insufficient amount**")
            return

        self.request = ctx.message
        embed = discord.Embed(title = f"[BETA]:coin:Coin flip for {ctx.author.name}",
                color= ctx.author.color,
                timestamp=datetime.utcnow())
        embed.add_field(name='Choose 🔵 or 🔴', value="Reward on win: 2x", inline=False)
        embed.add_field(name='Your Balance', value=str(points), inline=False)
        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
        r = await ctx.channel.send(embed=embed)
        await r.add_reaction("🔵")
        await r.add_reaction("🔴")


    @commands.Cog.listener() 
    async def on_reaction_add(self, reaction, user):
        if self.request.author==user and int(reaction.count)>1:
            channel = reaction.message.channel
            self.db.connect()
            player_points = self.db.getPoints(channel.guild.name, user.id) #get points of the player
            banker_points = self.db.getPoints(channel.guild.name, self.client.user.id) #get points of the player
            if games.Coinflip(self.bet, user, reaction).result:

                self.db.setPoints(channel.guild.name, self.client.user.id, banker_points-(self.bet*2))
                self.db.setPoints(channel.guild.name, user.id, player_points+self.bet)
                embed = discord.Embed(title = f"[BETA]:coin: : :white_check_mark: {user.name} **WON** with {reaction.emoji}",
                                        color= discord.Color.green(),
                                        timestamp=datetime.utcnow())
                embed.add_field(name='You won', value=f"**{str(self.bet*2)}** coins:moneybag:", inline=False)
                embed.add_field(name='Your new balance', value=f"**{str(player_points+self.bet)}** coins:moneybag:", inline=False)
                embed.set_footer(text=f'Requested by: {user.name}', icon_url=user.avatar_url)                                        
                await channel.send(embed=embed)
            else:
                self.db.setPoints(channel.guild.name, self.client.user.id, banker_points+self.bet)
                self.db.setPoints(channel.guild.name, user.id, player_points-self.bet)
                embed = discord.Embed(title = f"[BETA]:coin: : :x: {user.name} **LOST** with {reaction.emoji}",
                                        color= discord.Color.red(),
                                        timestamp=datetime.utcnow())
                embed.add_field(name='You lost', value=f"**{str(self.bet)}** coins:moneybag:", inline=False)
                embed.add_field(name='Your new balance', value=f"**{str(player_points-self.bet)}** coins:moneybag:", inline=False)
                embed.set_footer(text=f'Requested by: {user.name}', icon_url=user.avatar_url)                                        
                await channel.send(embed=embed)
            self.db.close_connection()
            await reaction.message.delete()
            
                 


def setup(client):
    client.add_cog(Games(client))
