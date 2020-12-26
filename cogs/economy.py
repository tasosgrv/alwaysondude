import discord
import logging
import math
import random
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
        await ctx.send(f":bank: {ctx.author.mention} has **{points}** points:moneybag:")

    @commands.command()
    async def leaderboard(self, ctx):
        async with ctx.message.channel.typing():
            embed = discord.Embed(title = f":bank: :bar_chart: Points Leaderboard for {ctx.guild.name}",
                            color= ctx.author.color,
                            timestamp=datetime.utcnow())
            self.db.connect()
            leaderboard = self.db.getLeaderboard(ctx.guild.name, 5, 0)
            self.db.close_connection()
            standings = ''
            for i,item in enumerate(leaderboard):
                standings += "" + str(i+1) + ". " + str(item[0]) + ": **" + str(item[1]) + "**\n"    
            embed.add_field(name='Top 5', 
                            value=standings,
                            inline=False
                            )
            embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def supply(self, ctx):
        async with ctx.message.channel.typing():
            self.db.connect()
            supply = self.db.getTotalSupply(ctx.guild.name)
            self.db.close_connection()
        await ctx.send(f":bank:: :bar_chart: **{ctx.guild.name}**  has a total supply of **{supply}** points:moneybag:")

    @commands.command()
    async def give(self, ctx, member, points):
        async with ctx.message.channel.typing():
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

    @give.error
    async def give_error(self, ctx, error):
        async with ctx.message.channel.typing():
            if isinstance(error, commands.MissingRequiredArgument):
                await ctx.send(f":bank:: :no_entry: **An argument is missing** \nCommand syntax: .give [member] [points]")

    
    @commands.command()
    async def rain(self, ctx, donation, number_of_members):
        try:    
            donation = int(donation)
            number_of_members = int(number_of_members)
        except ValueError:
            await ctx.channel.send(f":bank:: :no_entry: **The amount has to be an integer non negative number**")
            return
        
        if donation<1 or number_of_members<1:
            await ctx.channel.send(f":bank:: :no_entry: **The amount has to be an integer non negative number**")
            return

        self.db.connect()
        sender_amount= self.db.getPoints(ctx.guild.name, ctx.author.id)
        self.db.close_connection()
        if sender_amount<donation:
            await ctx.channel.send(f":bank:: :x: **Insufficient amount**")
            return

        members = await ctx.guild.fetch_members(limit=150).flatten()
        if number_of_members > len(members):
            await ctx.channel.send(f":bank:: :x: **Τhere are not so many members in this server**")
            return

        donation_share = math.floor(donation/number_of_members) #calculate the amount each user gets
        
        #pick the winners
        winners = []
        for m in range(number_of_members):
            winners.append(random.choice(members))

        embed = discord.Embed(title = f":bank:: :white_check_mark: {ctx.author.name} made a rain :cloud_rain: of **{donation}** points:moneybag:",
                        color= ctx.author.color,
                        timestamp=datetime.utcnow())
        respond = ""

        self.db.connect()
        self.db.setPoints(ctx.guild.name, ctx.author.id, sender_amount-donation) #decrease sender's points
        for winner in winners:
            recipient_amount= self.db.getPoints(ctx.guild.name, winner.id) 
            self.db.setPoints(ctx.guild.name, winner.id, recipient_amount+donation_share) #increase recipient's points
            respond += "\n"+ str(winner.mention ) + " got **" + str(donation_share) + "** points:moneybag:"
        
        self.db.close_connection()

        embed.add_field(name='Winners', 
                        value=respond,
                        inline=False
                        )
        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)
    
    @rain.error
    async def rain_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f":bank:: :no_entry: **An argument is missing** \nCommand syntax: .rain [total_amount] [numbers of recipients]")

    #TODO 1 Random pointS drop with reaction
    #TODO 3 Daily Point reward


            
def setup(client):
    client.add_cog(Economy(client))
