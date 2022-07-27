import discord
import math
import random
import re
from discord import emoji
from discord.errors import PrivilegedIntentsRequired
import games
import pprint as debug
from datetime import datetime
from discord.ext import tasks, commands
from discord_components import (
    Button,
    ButtonStyle,
)

class Games(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(aliases=['cp'])
    async def coinflip(self, ctx, bet):
        async def coinflip_callback(interaction):
            
            for component in interaction.message.components:
                for button in component:
                    button.disabled = True

            if interaction.user.id==ctx.author.id:

                coinflip = self.game.play(interaction.component.custom_id)

                player_points = self.client.db.getPoints(ctx.guild.name, ctx.author.id) #get points of the player
                if coinflip:    
                    self.client.db.transferPoints(ctx.guild.name, self.client.user.id, self.bet, ctx.author.id)
                    #self.client.db.betPlaced(channel.guild.name, user.id, self.bet, "coinflip", float(self.bet*2))
                    embed = discord.Embed(title = f":coin:Coinflip : :white_check_mark: {ctx.author.name} **WON** with {interaction.component.label}{interaction.component.emoji}",
                                            color= discord.Color.green(),
                                            timestamp=datetime.utcnow())
                    embed.add_field(name='You won', 
                                    value=f"**{str(self.bet)}** {self.client.db.getGuildValue(ctx.guild.id ,'currency_name')}{self.client.db.getGuildValue(ctx.guild.id ,'currency_emote')}", 
                                    inline=False)
                    embed.add_field(name='Your new balance', 
                                    value=f"**{str(player_points+self.bet)}** {self.client.db.getGuildValue(ctx.guild.id ,'currency_name')}{self.client.db.getGuildValue(ctx.guild.id ,'currency_emote')}", 
                                    inline=False)
                    embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
                              
                else:
                    self.client.db.transferPoints(ctx.guild.name, ctx.author.id, self.bet, self.client.user.id)
                    #self.client.db.betPlaced(channel.guild.name, user.id, self.bet, "coinflip", 0)
                    embed = discord.Embed(title = f":coin:Coinflip : :x: {ctx.author.name} **LOST** with {interaction.component.label}{interaction.component.emoji}",
                                            color= discord.Color.red(),
                                            timestamp=datetime.utcnow())
                    embed.add_field(name='You lost', 
                                    value=f"**{str(self.bet)}** {self.client.db.getGuildValue(ctx.guild.id ,'currency_name')}{self.client.db.getGuildValue(ctx.guild.id ,'currency_emote')}", 
                                    inline=False)
                    embed.add_field(name='Your new balance', 
                                    value=f"**{str(player_points-self.bet)}** {self.client.db.getGuildValue(ctx.guild.id ,'currency_name')}{self.client.db.getGuildValue(ctx.guild.id ,'currency_emote')}", 
                                    inline=False)
                    embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
                    

                await interaction.edit_origin(embed=embed, components=interaction.message.components)


        try:    
            self.bet = float(bet)
        except ValueError:
            await ctx.channel.send(f":coin: : :no_entry: **The amount has to be an non-negative number**")
            return
        
        if self.bet<1:
            await ctx.channel.send(f":coin: : :no_entry: **The amount has to be an non-negative number**")
            return


        points = self.client.db.getPoints(ctx.guild.name, ctx.author.id)


        if self.bet>points:
            await ctx.channel.send(f":coin: : :x: **Insufficient amount**")
            return

        self.game = games.Coinflip(bet, ctx.author)
        embed = discord.Embed(title = f":coin:Coinflip for {ctx.author.name}",
                color= ctx.author.color,
                timestamp=datetime.utcnow())
        embed.add_field(name="Choose Heads<:heads:850427517525688341> or Tails<:tails:850427660756451328> ", value="Reward on win: 2x", inline=False)
        embed.add_field(name='Your Balance', value=str(points), inline=False)
        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
        await ctx.message.reply(embed=embed,
            components=[[
                self.client.components_manager.add_callback(
                    Button(style=ButtonStyle.grey, label="Heads", id="heads", emoji=self.client.get_emoji(850427517525688341)), coinflip_callback),
                self.client.components_manager.add_callback(
                    Button(style=ButtonStyle.grey, label="Tails", id="tails", emoji=self.client.get_emoji(850427660756451328)), coinflip_callback),
            ]],
        )

    @coinflip.error
    async def coinflip_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.reply(
                embed=discord.Embed(
                    title=":coin:Coinflip : :no_entry: An argument is missing",
                    description=f"Command syntax: `{self.client.db.getGuildValue(ctx.guild.id, 'prefix')}coinflip [bet_amount]`",
                    color=discord.Color.red(),
                    )
                )

    
    @commands.command(aliases=['sl'])
    async def slot(self, ctx, bet):
        curr_name = self.client.db.getGuildValue(ctx.guild.id ,'currency_name')
        curr_emote = self.client.db.getGuildValue(ctx.guild.id ,'currency_emote')
        async def slot_callback(interaction):

            if interaction.user.id==ctx.author.id:

                player_points = self.client.db.getPoints(ctx.guild.name, ctx.author.id) #get points of the player

                if interaction.custom_id=="spin" and self.bet<=player_points:
                    slot = self.game.play()

                    self.client.db.transferPoints(ctx.guild.name, ctx.author.id, self.bet, self.client.user.id)

                    if slot[0]>0: #if player won
                        self.client.db.transferPoints(ctx.guild.name, self.client.user.id, slot[0]*self.bet, ctx.author.id)
                    
                    #self.client.db.betPlaced(channel.guild.name, user.id, self.bet, "slot", float(slot[0]*self.bet))
                    embed = discord.Embed(title = f":slot_machine: Slot Machine for {ctx.author.name}",
                            color= ctx.author.color,
                            timestamp=datetime.utcnow())
                    embed.add_field(name='Spin: '+str(self.game.counter), value=str(' '.join(map(str, slot[1]))), inline=False)
                    embed.add_field(name='Balance', value="**"+str(self.client.db.getPoints(ctx.guild.name, ctx.author.id))+f"**{curr_emote}", inline=True)
                    embed.add_field(name='You Won', value="**"+str(float(slot[0])*float(self.bet))+f"**{curr_emote}", inline=True)
                    embed.add_field(name='Multiplier', value=str(slot[0])+"x", inline=True)
                    embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
                      
                else: #not enough money to play message

                    for component in interaction.message.components:
                        for button in component:
                            button.disabled = True

                    embed = discord.Embed(title = f":slot_machine: :x: Slot Machine for {ctx.author.name}",
                            color= ctx.author.color,
                            timestamp=datetime.utcnow())
                    embed.add_field(name=':x: **Insufficient amount**', 
                                    value='You dont have **'+str(self.bet)+f'** {curr_name}{curr_emote} to play the next spin', 
                                    inline=False)
                    embed.add_field(name='Played', 
                                    value="**"+str(self.game.counter)+"** spins\n**"+str(self.game.counter*self.bet)+f"** {curr_name}{curr_emote}", 
                                    inline=True)
                    embed.add_field(name='Profit/Loss', 
                                    value="**"+str(self.game.profit_loss)+f"** {curr_name}{curr_emote}", 
                                    inline=True)
                    embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
            
                if interaction.custom_id=="stop":

                    for component in interaction.message.components:
                        for button in component:
                            button.disabled = True
                    
                    embed = discord.Embed(title = f":slot_machine: Slot Machine for {ctx.author.name}",
                            color= ctx.author.color,
                            timestamp=datetime.utcnow())
                    embed.add_field(name='Played', 
                                    value="**"+str(self.game.counter)+"** spins\n**"+str(self.game.counter*self.bet)+f"** {curr_name}{curr_emote}",
                                    inline=True)
                    embed.add_field(name='Profit/Loss', 
                                    value="**"+str(self.game.profit_loss)+f"** {curr_name}{curr_emote}", 
                                    inline=True)
                    embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
                    
                

            await interaction.edit_origin(embed=embed, components=interaction.message.components)

        try:    
            self.bet = float(bet)
        except ValueError:
            await ctx.channel.send(f":slot_machine: : :no_entry: **The amount has to be a non-negative number**")
            return
        
        if self.bet<0.10:
            await ctx.channel.send(f":slot_machine: : :no_entry: **The amount has to be a number over 0.10**")
            return


        points = self.client.db.getPoints(ctx.guild.name, ctx.author.id)

        if self.bet>points:
            await ctx.channel.send(f":slot_machine: : :x: **Insufficient amount**")
            return

        self.game = games.Slot(bet, ctx.author)
        
        embed = discord.Embed(title = f":slot_machine: Slot Machine for {ctx.author.name}",
                color= ctx.author.color,
                timestamp=datetime.utcnow())
        embed.add_field(name="How to play", value="Press the :repeat: to play\nPress the :stop_button: to stop", inline=False)
        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
        await ctx.message.reply(embed=embed,
            components=[[
                self.client.components_manager.add_callback(
                    Button(style=ButtonStyle.green, label="Spin", id="spin", emoji="🔁"), slot_callback),
                self.client.components_manager.add_callback(
                    Button(style=ButtonStyle.red, label="Stop", id="stop", emoji="⏹"), slot_callback),
            ]],
        )

    @slot.error
    async def slot_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.reply(
                embed=discord.Embed(
                    title=":slot_machine: Slot Machine : :no_entry: An argument is missing",
                    description=f"Command syntax: `{self.client.db.getGuildValue(ctx.guild.id, 'prefix')}slot [bet_amount]`",
                    color=discord.Color.red(),
                    )
                )


    @commands.command(aliases=['ftk'])
    async def findtheking(self, ctx, bet):

        async def ftk_callback(interaction):
            if interaction.user.id==ctx.author.id:

                player_points = self.client.db.getPoints(ctx.guild.name, ctx.author.id) #get points of the player
                ftk = self.game.play(interaction.custom_id)
                contnt = f"{str(' '.join(map(str, ftk[1])))}"
                if ftk[0]:
                    self.client.db.transferPoints(ctx.guild.name, self.client.user.id, self.bet*3, ctx.author.id)
                    embed = discord.Embed(title = f"<:cardSpadesK:853266560361824256>Find The King : :white_check_mark: {ctx.author.name} WON with {interaction.component.emoji}{interaction.component.label}",
                        color= discord.Color.green(),
                        timestamp=datetime.utcnow())
                    embed.add_field(name="You won", value="**"+str(self.bet*3)+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=False)
                    embed.add_field(name='Your new Balance', value="**"+str(player_points+self.bet*3)+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=False)
                    embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
                else:
                    self.client.db.transferPoints(ctx.guild.name, ctx.author.id, self.bet, self.client.user.id)
                    embed = discord.Embed(title = f"<:cardSpadesK:853266560361824256>Find The King : :x: {ctx.author.name} LOST with {interaction.component.emoji}{interaction.component.label}",
                        color= discord.Color.red(),
                        timestamp=datetime.utcnow())
                    embed.add_field(name="You lost", value="**"+str(self.bet)+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=False)
                    embed.add_field(name='Your Balance', value="**"+str(player_points-self.bet)+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=False)
                    embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)

            
            for component in interaction.message.components:
                for button in component:
                    button.disabled = True

            await interaction.edit_origin(content=contnt, embed=embed, components=interaction.message.components)


        try:    
            self.bet = float(bet)
        except ValueError:
            await ctx.channel.send(f"<:cardSpadesK:853266560361824256>: **The amount has to be a non-negative number**")
            return
        
        if self.bet<1:
            await ctx.channel.send(f"<:cardSpadesK:853266560361824256>  :no_entry: **The amount has to be a number over 1**")
            return


        points = self.client.db.getPoints(ctx.guild.name, ctx.author.id)


        if self.bet>points:
            await ctx.channel.send(f"<:cardSpadesK:853266560361824256> :x: **Insufficient amount**")
            return

        self.game = games.FindTheKing(bet, ctx.author)
        
        embed = discord.Embed(title = f"<:cardSpadesK:853266560361824256>Find The King for {ctx.author.name}",
                color= ctx.author.color,
                timestamp=datetime.utcnow())
        embed.add_field(name="Choose Red<:cardBackRed:853266658084782090>, Green<:cardBackGreen:853266658201436190>, or Blue<:cardBackBlue:853266657715027998> ", value="Reward on win: 3x", inline=False)
        embed.add_field(name='Your Balance', value=str(points), inline=False)
        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
        await ctx.message.reply(
            content=f"<:cardBackRed:853266658084782090> <:cardBackGreen:853266658201436190> <:cardBackBlue:853266657715027998>" , 
            embed=embed,
            components=[[
                self.client.components_manager.add_callback(
                Button(style=ButtonStyle.red, label="Red", id="red", emoji=self.client.get_emoji(853266658084782090)), ftk_callback),
                self.client.components_manager.add_callback(
                Button(style=ButtonStyle.green, label="Green", id="green", emoji=self.client.get_emoji(853266658201436190)), ftk_callback),
                self.client.components_manager.add_callback(
                Button(style=ButtonStyle.blue, label="Blue", id="blue", emoji=self.client.get_emoji(853266657715027998)), ftk_callback),
            ]],
        )
        

    @findtheking.error
    async def findtheking_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.reply(
                embed=discord.Embed(
                    title=f"<:cardSpadesK:853266560361824256>Find The King : :no_entry: An argument is missing",
                    description=f"Command syntax: `{self.client.db.getGuildValue(ctx.guild.id, 'prefix')}ftk [bet_amount]`",
                    color=discord.Color.red(),
                    )
                )


    @commands.command(aliases=['d'])
    async def dice(self, ctx, bet): #TODO Dice game
        try:    
            self.bet = float(bet)
        except ValueError:
            await ctx.channel.send(f"**Dice - The amount has to be a non-negative number**")
            return
        
        if self.bet<1:
            await ctx.channel.send(f"**Dice :no_entry: The amount has to be a number over 1**")
            return


        points = self.client.db.getPoints(ctx.guild.name, ctx.author.id)


        if self.bet>points:
            await ctx.channel.send(f"**Dice :x: Insufficient amount**")
            return

        self.game = games.Dice(bet, ctx.author)
        results = self.game.play()

        dices = {
            '1':'<:dicered1:832673661696868353>',
            '2':'<:dicered2:832673662078812192>',
            '3':'<:dicered3:832673662217748530>',
            '4':'<:dicered4:832673662288265236>',
            '5':'<:dicered5:832673662296916068>',
            '6':'<:dicered6:832673662205296641>'
        }


        if results[0]>1:
            self.client.db.transferPoints(ctx.guild.name, self.client.user.id, results[0]*self.bet, ctx.author.id)
            embed = discord.Embed(title = f"Dice for {ctx.author.name}",
            color= discord.Color.green(),
            timestamp=datetime.utcnow())
        elif results[0]>0:
            embed = discord.Embed(title = f"Dice for {ctx.author.name}",
            color= discord.Color.orange(),
            timestamp=datetime.utcnow())
        else:
            self.client.db.transferPoints(ctx.guild.name, ctx.author.id, self.bet, self.client.user.id)
            embed = discord.Embed(title = f"Dice for {ctx.author.name}",
            color= discord.Color.red(),
            timestamp=datetime.utcnow())

        embed.add_field(name=f"You Rolled ({str(results[1][0]+results[1][1])}):", value=f"{dices[str(results[1][0])]} {dices[str(results[1][1])]}", inline=False)
        embed.add_field(name="You won:", value="**"+str(float(self.bet*results[0]))+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=True)
        embed.add_field(name="Your Balance:", value="**"+str(self.client.db.getPoints(ctx.guild.name, ctx.author.id))+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=True)
        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)

        r = await ctx.message.reply(embed=embed)


    @dice.error
    async def dice_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.reply(
                embed=discord.Embed(
                    title="Dice : :no_entry: An argument is missing",
                    description=f"Command syntax: `{self.client.db.getGuildValue(ctx.guild.id, 'prefix')}dice [bet_amount]`",
                    color=discord.Color.red(),
                    )
                )

    
    @commands.command(aliases=['bj'])
    async def blackjack(self, ctx, bet): #TODO Black Jack game
        
        async def bj_callback(interaction):
            if interaction.user.id==ctx.author.id:

                player_points = self.client.db.getPoints(ctx.guild.name, ctx.author.id) #get points of the player


                if interaction.custom_id=="hit":
                    
                    if self.game.hit():
                        
                        if self.game.player_score==21:

                            for component in interaction.message.components:
                                for button in component:
                                    button.disabled = True
                            interaction.custom_id="stand"
                        else:   
                            embed = discord.Embed(title = f"BlackJack for {ctx.author.name}",
                                color= ctx.author.color,
                                timestamp=datetime.utcnow())
                            embed.add_field(name="Player Cards", value="**"+ re.sub("', '|\['|\']", " ", str([x.detailed_info() for x in self.game.player])) + "**\nValue: **"+ str(self.game.player_score) +"**", inline=True)
                            embed.add_field(name='Banker Cards', value="**"+ re.sub("', '|\['|\']", " ", str([x.detailed_info() for x in self.game.banker])) + "**\nValue: **"+ str(self.game.banker_score) +"**", inline=True)
                            embed.add_field(name='Your bet', value="**"+str(self.bet)+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=False)
                            embed.add_field(name='Balance', value="**"+str(player_points)+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=True)
                            embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)

                            for component in interaction.message.components:
                                for button in component:
                                    if button.custom_id=="double":
                                        button.disabled = True

                    else: #burned
                        embed = discord.Embed(title = f"BlackJack : {ctx.author.name} :x:LOST with {str(self.game.player_score)}",
                            color=discord.Color.red(),
                            timestamp=datetime.utcnow())
                        embed.add_field(name="Player Cards", value="**"+ re.sub("', '|\['|\']", " ", str([x.detailed_info() for x in self.game.player])) + "**\nValue: **"+ str(self.game.player_score) +"**", inline=True)
                        embed.add_field(name='Banker Cards', value="**"+ re.sub("', '|\['|\']", " ", str([x.detailed_info() for x in self.game.banker])) + "**\nValue: **"+ str(self.game.banker_score) +"**", inline=True)
                        embed.add_field(name="You won:", value="**" + str(float(self.bet*0))+ "**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=False)
                        embed.add_field(name='Balance', value="**"+str(player_points)+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote')
                        
                        , inline=True)
                        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)

                        for component in interaction.message.components:
                            for button in component:
                                button.disabled = True

                if interaction.custom_id=="double":
                    self.bet = self.bet*2

                    self.client.db.transferPoints(ctx.guild.name,  ctx.author.id, self.bet, self.client.user.id)

                    
                    if self.game.hit():
                        interaction.custom_id="stand"

                    else: #burned
                        embed = discord.Embed(title = f"BlackJack : {ctx.author.name} :x:LOST with {str(self.game.player_score)}",
                            color=discord.Color.red(),
                            timestamp=datetime.utcnow())
                        embed.add_field(name="Player Cards", value="**"+ re.sub("', '|\['|\']", " ", str([x.detailed_info() for x in self.game.player])) + "**\nValue: **"+ str(self.game.player_score) +"**", inline=True)
                        embed.add_field(name='Banker Cards', value="**"+ re.sub("', '|\['|\']", " ", str([x.detailed_info() for x in self.game.banker])) + "**\nValue: **"+ str(self.game.banker_score) +"**", inline=True)
                        embed.add_field(name="You won:", value="**"+str(float(self.bet*0))+"**"+self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=False)
                        embed.add_field(name='Balance', value="**"+str(player_points)+"**"+self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=True)
                        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)                     

                        for component in interaction.message.components:
                            for button in component:
                                button.disabled = True
                    

                if interaction.custom_id=="stand":

                    for component in interaction.message.components:
                        for button in component:
                            button.disabled = True

                    mullti = self.game.stand()
                    if mullti==2:

                        self.client.db.transferPoints(ctx.guild.name, self.client.user.id, self.bet*2, ctx.author.id)

                        embed = discord.Embed(title = f"BlackJack : {ctx.author.name} :white_check_mark:WON with {str(self.game.player_score)}",
                            color=discord.Color.green(),
                            timestamp=datetime.utcnow())
                        embed.add_field(name="Player Cards", value="**"+ re.sub("', '|\['|\']", " ", str([x.detailed_info() for x in self.game.player])) + "**\nValue: **"+ str(self.game.player_score) +"**", inline=True)
                        embed.add_field(name='Banker Cards', value="**"+ re.sub("', '|\['|\']", " ", str([x.detailed_info() for x in self.game.banker])) + "**\nValue: **"+ str(self.game.banker_score) +"**", inline=True)
                        embed.add_field(name="You won:", value="**"+str(float(self.bet*2))+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=False)
                        embed.add_field(name='Balance', value="**"+str(player_points+self.bet*2)+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=True)
                        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
                    elif mullti==1: #draw

                        self.client.db.transferPoints(ctx.guild.name, self.client.user.id, self.bet, ctx.author.id)

                        embed = discord.Embed(title = f"BlackJack : {ctx.author.name} DRAW with {str(self.game.player_score)}",
                            color=discord.Color.gold(),
                            timestamp=datetime.utcnow())
                        embed.add_field(name="Player Cards", value="**"+ re.sub("', '|\['|\']", " ", str([x.detailed_info() for x in self.game.player])) + "**\nValue: **"+ str(self.game.player_score) +"**", inline=True)
                        embed.add_field(name='Banker Cards', value="**"+ re.sub("', '|\['|\']", " ", str([x.detailed_info() for x in self.game.banker])) + "**\nValue: **"+ str(self.game.banker_score) +"**", inline=True)
                        embed.add_field(name="You won:", value="**"+str(float(self.bet))+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=False)
                        embed.add_field(name='Balance', value="**"+str(player_points+self.bet)+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote') , inline=True)
                        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)                       
                    else:    #lost
                        embed = discord.Embed(title = f"BlackJack : {ctx.author.name} :x:LOST with {str(self.game.player_score)}",
                            color=discord.Color.red(),
                            timestamp=datetime.utcnow())
                        embed.add_field(name="Player Cards", value="**"+ re.sub("', '|\['|\']", " ", str([x.detailed_info() for x in self.game.player])) + "**\nValue: **"+ str(self.game.player_score) +"**", inline=True)
                        embed.add_field(name='Banker Cards', value="**"+ re.sub("', '|\['|\']", " ", str([x.detailed_info() for x in self.game.banker])) + "**\nValue: **"+ str(self.game.banker_score) +"**", inline=True)
                        embed.add_field(name="You won:", value="**"+str(float(self.bet*0))+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=False)
                        embed.add_field(name='Balance', value="**"+str(player_points)+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=True)
                        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
    


                await interaction.edit_origin(embed=embed, components=interaction.message.components)

            

        try:    
            self.bet = float(bet)
        except ValueError:
            await ctx.channel.send(f"**BlackJack - The amount has to be a non-negative number**")
            return
        
        if self.bet<1:
            await ctx.channel.send(f"**BlackJack :no_entry: The amount has to be a number over 1**")
            return


        points = self.client.db.getPoints(ctx.guild.name, ctx.author.id)


        if self.bet>points:
            await ctx.channel.send(f"**BlackJack :x: Insufficient amount**")
            return

        self.game = games.BlackJack(bet, ctx.author)


        self.client.db.transferPoints(ctx.guild.name,  ctx.author.id, self.bet, self.client.user.id)

        
        if self.game.play()==21:

            self.client.db.transferPoints(ctx.guild.name, self.client.user.id, 2.2*self.bet, ctx.author.id)

            embed = discord.Embed(title = f"BlackJack: {ctx.author.name} :white_check_mark:WON with BLACK JACK",
                        color= discord.Color.green(),
                        timestamp=datetime.utcnow())
            embed.add_field(name="Player Cards", value="**"+ re.sub("', '|\['|\']", " ", str([x.detailed_info() for x in self.game.player])) + "**\nValue: **"+ str(self.game.player_score) +"**", inline=True)
            embed.add_field(name='Banker Cards', value="**"+ re.sub("', '|\['|\']", " ", str([x.detailed_info() for x in self.game.banker])) + "**\nValue: **"+ str(self.game.banker_score) +"**", inline=True)
            embed.add_field(name="You won:", value="**"+str(float(self.bet*2.2))+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=False)
            embed.add_field(name='Balance', value="**"+str(points+float(self.bet*2.2))+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=True)
            embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
            await ctx.message.reply(embed=embed)               

        else: # bj setup for reaction
            embed = discord.Embed(title = f"Game BlackJack for {ctx.author.name}",
                    color= ctx.author.color,
                    timestamp=datetime.utcnow())
            embed.add_field(name="Player Cards", value="**"+ re.sub("', '|\['|\']", " ", str([x.detailed_info() for x in self.game.player])) + "**\nValue: **"+ str(self.game.player_score) +"**", inline=True)
            embed.add_field(name='Banker Cards', value="**"+ re.sub("', '|\['|\']", " ", str([x.detailed_info() for x in self.game.banker])) + "**\nValue: **"+ str(self.game.banker_score) +"**", inline=True)
            embed.add_field(name='Your bet', value="**"+str(self.bet)+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=False)
            embed.add_field(name='Balance', value="**"+str(points)+"**" + self.client.db.getGuildValue(ctx.guild.id, 'currency_emote'), inline=True)
            embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
            await ctx.message.reply(
                embed=embed,            
                components=[[
                    self.client.components_manager.add_callback(
                    Button(style=ButtonStyle.green, label="Hit", id="hit", emoji="✔"), bj_callback),
                    self.client.components_manager.add_callback(
                    Button(style=ButtonStyle.red, label="Stand", id="stand", emoji="✋"), bj_callback),
                    self.client.components_manager.add_callback(
                    Button(style=ButtonStyle.grey, label="Double", id="double", emoji="⏫"), bj_callback),
                ]]
            )

    @blackjack.error
    async def blackjack_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.reply(
                embed=discord.Embed(
                    title="BlackJack : :no_entry: An argument is missing",
                    description="Command syntax: `.blackjack [bet_amount]`",
                    color=discord.Color.red(),
                    )
                )


def setup(client):
    client.add_cog(Games(client))
