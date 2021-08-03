import discord
import math
import random
import re
import database
import games
import asyncio
import pprint as debug
from datetime import datetime
from discord.ext import tasks, commands

class Games(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.db = database.Database()

    
    @commands.command(aliases=['cp'])
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

        self.game = games.Coinflip(bet, ctx.author)
        embed = discord.Embed(title = f"Game :coin:Coin flip for {ctx.author.name}",
                color= ctx.author.color,
                timestamp=datetime.utcnow())
        embed.add_field(name="Choose Heads<:heads:850427517525688341> or Tails<:tails:850427660756451328> ", value="Reward on win: 2x", inline=False)
        embed.add_field(name='Your Balance', value=str(points), inline=False)
        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
        r = await ctx.message.reply(embed=embed)
        await r.add_reaction("<:heads:850427517525688341>")
        await r.add_reaction("<:tails:850427660756451328>")

    @coinflip.error
    async def coinflip_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f":coin: : :no_entry: **An argument is missing** \nCommand syntax: .coinflip [bet_amount]")

    @commands.command(aliases=['sl'])
    async def slot(self, ctx, bet):
        try:    
            self.bet = float(bet)
        except ValueError:
            await ctx.channel.send(f":slot_machine: : :no_entry: **The amount has to be a non-negative number**")
            return
        
        if self.bet<0.10:
            await ctx.channel.send(f":slot_machine: : :no_entry: **The amount has to be a number over 0.10**")
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
        embed.add_field(name="How to play", value="Press the :repeat: to play\nPress the :stop_button: to stop", inline=False)
        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
        r = await ctx.message.reply(embed=embed)
        await r.add_reaction("🔁")
        await r.add_reaction("⏹️")

    @slot.error
    async def slot_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f":slot_machine: : :no_entry: **An argument is missing** \nCommand syntax: .slot [bet_amount]")


    @commands.command(aliases=['ftk'])
    async def findtheking(self, ctx, bet): #TODO Find The King game
        try:    
            self.bet = float(bet)
        except ValueError:
            await ctx.channel.send(f"<:cardSpadesK:853266560361824256>: **The amount has to be a non-negative number**")
            return
        
        if self.bet<1:
            await ctx.channel.send(f"<:cardSpadesK:853266560361824256>  :no_entry: **The amount has to be a number over 1**")
            return

        self.db.connect()
        points = self.db.getPoints(ctx.guild.name, ctx.author.id)
        self.db.close_connection()

        if self.bet>points:
            await ctx.channel.send(f"<:cardSpadesK:853266560361824256> :x: **Insufficient amount**")
            return

        self.game = games.FindTheKing(bet, ctx.author)
        
        embed = discord.Embed(title = f"Game <:cardSpadesK:853266560361824256> Find The King for {ctx.author.name}",
                color= ctx.author.color,
                timestamp=datetime.utcnow())
        embed.add_field(name="Choose Red<:cardBackRed:853266658084782090>, Green<:cardBackGreen:853266658201436190>, or Blue<:cardBackBlue:853266657715027998> ", value="Reward on win: 3x", inline=False)
        embed.add_field(name='Your Balance', value=str(points), inline=False)
        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
        r = await ctx.message.reply(content=f"<:cardBackRed:853266658084782090> <:cardBackGreen:853266658201436190> <:cardBackBlue:853266657715027998>" , embed=embed)
        await r.add_reaction("<:cardBackRed:853266658084782090>")
        await r.add_reaction("<:cardBackGreen:853266658201436190>")
        await r.add_reaction("<:cardBackBlue:853266657715027998>")



    @findtheking.error
    async def findtheking_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"<:cardSpadesK:849958109459382303> : :no_entry: **An argument is missing** \nCommand syntax: .ftk [bet_amount]")


    @commands.command(aliases=['d'])
    async def dice(self, ctx, bet): #TODO Dice game
        pass

    @commands.command(aliases=['bj'])
    async def blackjack(self, ctx, bet): #TODO Black Jack game
        pass

    @commands.Cog.listener() 
    async def on_reaction_add(self, reaction, user):

        channel = reaction.message.channel
        try:
            request = await channel.fetch_message(reaction.message.reference.message_id)
            contnt = reaction.message.content
        except AttributeError:
            return
        
        if request.author==user and int(reaction.count)>1:
            self.db.connect()
            player_points = self.db.getPoints(channel.guild.name, user.id) #get points of the player
            banker_points = self.db.getPoints(channel.guild.name, self.client.user.id) #get points of the banker
            
            if request.content.startswith('.sl'): #SLOT
                if reaction.emoji=="🔁" and self.bet<=player_points:
                    slot = self.game.play()
                    
                    await reaction.message.remove_reaction(reaction.emoji, user)

                    self.db.transferPoints(channel.guild.name, user.id, self.bet, self.client.user.id)

                    if slot[0]>0: #if player won
                        self.db.transferPoints(channel.guild.name, self.client.user.id, slot[0]*self.bet, user.id)
                    
                    #self.db.betPlaced(channel.guild.name, user.id, self.bet, "slot", float(slot[0]*self.bet))
                    embed = discord.Embed(title = f"[BETA] :slot_machine: Slot Machine for {user.name}",
                            color= user.color,
                            timestamp=datetime.utcnow())
                    embed.add_field(name='Spin: '+str(self.game.counter), value=str(' '.join(map(str, slot[1]))), inline=False)
                    embed.add_field(name='Balance', value="**"+str(self.db.getPoints(channel.guild.name, user.id))+"**:moneybag:", inline=True)
                    embed.add_field(name='You Won', value="**"+str(float(slot[0])*float(self.bet))+"**:moneybag:", inline=True)
                    embed.add_field(name='Multiplier', value=str(slot[0])+"x", inline=True)
                    embed.set_footer(text=f'Requested by: {user.name}', icon_url=user.avatar_url)
                    
                
                else: #not enough money to play message
                    embed = discord.Embed(title = f"[BETA]:slot_machine: :x: Slot Machine for {user.name}",
                            color= user.color,
                            timestamp=datetime.utcnow())
                    embed.add_field(name=':x: **Insufficient amount**', 
                                    value='You dont have **'+str(self.bet)+'** coins:moneybag: to play the next spin', 
                                    inline=False)
                    embed.add_field(name='Played', 
                                    value="**"+str(self.game.counter)+"** spins\n**"+str(self.game.counter*self.bet)+"** coins :moneybag:", 
                                    inline=True)
                    embed.set_footer(text=f'Requested by: {user.name}', icon_url=user.avatar_url)
                    await reaction.message.clear_reactions()
                
                if reaction.emoji=="⏹️":
                    embed = discord.Embed(title = f"[BETA]:slot_machine: Slot Machine for {user.name}",
                            color= user.color,
                            timestamp=datetime.utcnow())
                    embed.add_field(name='Played', 
                                    value="**"+str(self.game.counter)+"** spins\n**"+str(self.game.counter*self.bet)+"** coins :moneybag:",
                                    inline=True)
                    embed.set_footer(text=f'Requested by: {user.name}', icon_url=user.avatar_url)
                    await reaction.message.clear_reactions()
                self.db.close_connection()
            
            elif  request.content.startswith('.c'): #COINFLIP
                coinflip = self.game.play(reaction)
                if coinflip:
                    self.db.transferPoints(channel.guild.name, self.client.user.id, self.bet, user.id)
                    #self.db.betPlaced(channel.guild.name, user.id, self.bet, "coinflip", float(self.bet*2))
                    embed = discord.Embed(title = f"[BETA]:coin: : :white_check_mark: {user.name} **WON** with {reaction.emoji.name}{reaction.emoji}",
                                            color= discord.Color.green(),
                                            timestamp=datetime.utcnow())
                    embed.add_field(name='You won', 
                                    value=f"**{str(self.bet)}** coins:moneybag:", 
                                    inline=False)
                    embed.add_field(name='Your new balance', 
                                    value=f"**{str(player_points+self.bet)}** coins:moneybag:", 
                                    inline=False)
                    embed.set_footer(text=f'Requested by: {user.name}', icon_url=user.avatar_url)
                    await reaction.message.clear_reactions()                                 
                else:
                    self.db.transferPoints(channel.guild.name, user.id, self.bet, self.client.user.id)
                    self.db.betPlaced(channel.guild.name, user.id, self.bet, "coinflip", 0)
                    embed = discord.Embed(title = f"[BETA]:coin: : :x: {user.name} **LOST** with {reaction.emoji.name}{reaction.emoji}",
                                            color= discord.Color.red(),
                                            timestamp=datetime.utcnow())
                    embed.add_field(name='You lost', 
                                    value=f"**{str(self.bet)}** coins:moneybag:", 
                                    inline=False)
                    embed.add_field(name='Your new balance', 
                                    value=f"**{str(player_points-self.bet)}** coins:moneybag:", 
                                    inline=False)
                    embed.set_footer(text=f'Requested by: {user.name}', icon_url=user.avatar_url)
                    await reaction.message.clear_reactions()                                       
                self.db.close_connection()
            
            elif request.content.startswith('.f'):
                ftk = self.game.play(reaction)
                await reaction.message.clear_reactions()
                contnt = f"{str(' '.join(map(str, ftk[1])))}"
                if ftk[0]:
                    self.db.transferPoints(channel.guild.name, self.client.user.id, self.bet*3, user.id)
                    embed = discord.Embed(title = f"Game <:cardSpadesK:853266560361824256> : :white_check_mark: {user.name} WON with {reaction.emoji}",
                        color= discord.Color.green(),
                        timestamp=datetime.utcnow())
                    embed.add_field(name="You won", value="**"+str(self.bet*3)+"** :moneybag:", inline=False)
                    embed.add_field(name='Your new Balance', value="**"+str(player_points+self.bet*3)+"** :moneybag:", inline=False)
                    embed.set_footer(text=f'Requested by: {user.name}', icon_url=user.avatar_url)
                else:
                    self.db.transferPoints(channel.guild.name, user.id, self.bet, self.client.user.id)
                    embed = discord.Embed(title = f"Game <:cardSpadesK:853266560361824256> : :x: {user.name} LOST with {reaction.emoji}",
                        color= discord.Color.red(),
                        timestamp=datetime.utcnow())
                    embed.add_field(name="You lost", value="**"+str(self.bet)+"** :moneybag:", inline=False)
                    embed.add_field(name='Your Balance', value="**"+str(player_points-self.bet)+"** :moneybag:", inline=False)
                    embed.set_footer(text=f'Requested by: {user.name}', icon_url=user.avatar_url)

            else: return
            await reaction.message.edit(content=contnt, embed=embed) 
            
                 


def setup(client):
    client.add_cog(Games(client))
