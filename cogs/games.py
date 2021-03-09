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
            self.bet = float(bet)
        except ValueError:
            await ctx.channel.send(f":coin: : :no_entry: **The amount has to be an non-negative number**")
            return
        
        if self.bet<1:
            await ctx.channel.send(f":coin: : :no_entry: **The amount has to be an non-negative number**")
            return

        self.db.connect()
        points = self.db.getPoints(ctx.guild.name, ctx.author.id)
        self.db.close_connection()

        if self.bet>points:
            await ctx.channel.send(f":coin: : :x: **Insufficient amount**")
            return

        self.request = ctx.message
        embed = discord.Embed(title = f"Game :coin:Coin flip for {ctx.author.name}",
                color= ctx.author.color,
                timestamp=datetime.utcnow())
        embed.add_field(name='Choose 🔵 or 🔴', value="Reward on win: 2x", inline=False)
        embed.add_field(name='Your Balance', value=str(points-self.bet), inline=False)
        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
        r = await ctx.message.reply(embed=embed)
        await r.add_reaction("🔵")
        await r.add_reaction("🔴")

    @coinflip.error
    async def coinflip_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f":coin: : :no_entry: **An argument is missing** \nCommand syntax: .coinflip [bet_amount]")

    @commands.command()
    async def slot(self, ctx, bet):
        try:    
            self.bet = float(bet)
        except ValueError:
            await ctx.channel.send(f":slot_machine: : :no_entry: **The amount has to be a non-negative number**")
            return
        
        if self.bet<1:
            await ctx.channel.send(f":slot_machine: : :no_entry: **The amount has to be a non-negative number**")
            return

        self.db.connect()
        points = self.db.getPoints(ctx.guild.name, ctx.author.id)
        self.db.close_connection()

        if self.bet>points:
            await ctx.channel.send(f":slot_machine: : :x: **Insufficient amount**")
            return

        self.game = games.Slot(bet, ctx.author)
        
        embed = discord.Embed(title = f"[BETA]:slot_machine: Slot Machine for {ctx.author.name}",
                color= ctx.author.color,
                timestamp=datetime.utcnow())
        embed.add_field(name="How to play", value="Press the :repeat: to play\nPress the :stop_button: to play", inline=False)
        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
        r = await ctx.message.reply(embed=embed)
        await r.add_reaction("🔁")
        await r.add_reaction("⏹️")

    @commands.Cog.listener() 
    async def on_reaction_add(self, reaction, user):
        
        channel = reaction.message.channel
        try:
            request = await channel.fetch_message(reaction.message.reference.message_id)
        except AttributeError:
            return
        
        if request.author==user and int(reaction.count)>1:
            self.db.connect()
            player_points = self.db.getPoints(channel.guild.name, user.id) #get points of the player
            banker_points = self.db.getPoints(channel.guild.name, self.client.user.id) #get points of the player
            
            if ".slot" in request.content:
                if reaction.emoji=="🔁":
                    slot = self.game.play()
                    
                    self.db.setPoints(channel.guild.name, user.id, player_points-self.bet)
                    self.db.setPoints(channel.guild.name, self.client.user.id, banker_points+self.bet)
                    if slot[0]>0:
                        self.db.setPoints(channel.guild.name, user.id, player_points+(slot[0]*self.bet))
                        self.db.setPoints(channel.guild.name, self.client.user.id, banker_points+(slot[0]*self.bet))
                    
                    embed = discord.Embed(title = f"[BETA] :slot_machine: Slot Machine for {user.name}",
                            color= user.color,
                            timestamp=datetime.utcnow())
                    embed.add_field(name='Spin: '+str(self.game.counter), value=str(' '.join(map(str, slot[1]))), inline=False)
                    embed.add_field(name='Balance', value="**"+str(float(player_points) + (float(slot[0])*float(self.bet)))+"**:moneybag:", inline=True)
                    embed.add_field(name='You Won', value="**"+str(float(slot[0])*float(self.bet))+"**:moneybag:", inline=True)
                    embed.add_field(name='Multiplier', value=str(slot[0])+"x", inline=True)
                    embed.set_footer(text=f'Requested by: {user.name}', icon_url=user.avatar_url)
                    await reaction.message.remove_reaction(reaction.emoji, user)
                if reaction.emoji=="⏹️":
                    embed = discord.Embed(title = f"[BETA]:slot_machine: Slot Machine for {user.name}",
                            color= user.color,
                            timestamp=datetime.utcnow())
                    embed.add_field(name='Played', value="**"+str(self.game.counter)+"** spins\n**"+str(self.game.counter*self.bet)+"** coins :moneybag:", inline=True)
                    embed.set_footer(text=f'Requested by: {user.name}', icon_url=user.avatar_url)
                    await reaction.message.clear_reactions()
                self.db.close_connection()
            else:
                if games.Coinflip(self.bet, user, reaction).result:
                    self.db.setPoints(channel.guild.name, self.client.user.id, banker_points-self.bet)
                    self.db.setPoints(channel.guild.name, user.id, player_points+self.bet)
                    embed = discord.Embed(title = f"[BETA]:coin: : :white_check_mark: {user.name} **WON** with {reaction.emoji}",
                                            color= discord.Color.green(),
                                            timestamp=datetime.utcnow())
                    embed.add_field(name='You won', value=f"**{str(self.bet*2)}** coins:moneybag:", inline=False)
                    embed.add_field(name='Your new balance', value=f"**{str(player_points+self.bet)}** coins:moneybag:", inline=False)
                    embed.set_footer(text=f'Requested by: {user.name}', icon_url=user.avatar_url)
                    await reaction.message.clear_reactions()                                 
                else:
                    self.db.setPoints(channel.guild.name, user.id, player_points-self.bet)
                    self.db.setPoints(channel.guild.name, self.client.user.id, banker_points+self.bet)
                    embed = discord.Embed(title = f"[BETA]:coin: : :x: {user.name} **LOST** with {reaction.emoji}",
                                            color= discord.Color.red(),
                                            timestamp=datetime.utcnow())
                    embed.add_field(name='You lost', value=f"**{str(self.bet)}** coins:moneybag:", inline=False)
                    embed.add_field(name='Your new balance', value=f"**{str(player_points-self.bet)}** coins:moneybag:", inline=False)
                    embed.set_footer(text=f'Requested by: {user.name}', icon_url=user.avatar_url)
                    await reaction.message.clear_reactions()                                       
                self.db.close_connection()
            await reaction.message.edit(embed=embed) 
            
                 


def setup(client):
    client.add_cog(Games(client))
