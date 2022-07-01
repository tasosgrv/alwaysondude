import discord
from discord.ext import tasks, commands
from discord_components import (
    Button,
    ButtonStyle,
)
import math
import random
import re
import database
import pprint as debug
from datetime import datetime, timedelta



class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.db = database.Database()
        self.reward.start()

    @commands.command(aliases=['bal', 'b'])
    async def balance(self, ctx):
        await ctx.message.reply(f":bank: {ctx.author.mention} has **{self.db.getPoints(ctx.guild.name, ctx.author.id)}** {self.db.getGuildValue(ctx.guild.id ,'currency_name')}{self.db.getGuildValue(ctx.guild.id ,'currency_emote')}")

    @commands.command(aliases=['leadr', 'l'])
    async def leaderboard(self, ctx):
        async with ctx.message.channel.typing():
            embed = discord.Embed(title = f":bank: :bar_chart: {self.db.getGuildValue(ctx.guild.id ,'currency_name')} Leaderboard for {ctx.guild.name}",
                            color= ctx.author.color,
                            timestamp=datetime.utcnow())

            leaderboard = self.db.getLeaderboard(ctx.guild.name, 10, 0)

            standings = ''
            for i,item in enumerate(leaderboard):
                standings += "" + str(i+1) + ". " + str(item[0]) + ": **" + str(item[1]) + "**\n"    
            embed.add_field(name='Top 10', 
                            value=standings,
                            inline=False
                            )
            embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def supply(self, ctx):
        async with ctx.message.channel.typing():

            circ_supply = self.db.getCirculatingSupply(ctx.guild.name)
            max_supply = self.db.getTotalSupply(ctx.guild.name)

        await ctx.send(f":bank:: :bar_chart: **{ctx.guild.name}** has **{circ_supply}** {self.db.getGuildValue(ctx.guild.id ,'currency_name')}{self.db.getGuildValue(ctx.guild.id ,'currency_emote')} Circulating Supply and **{max_supply}** {self.db.getGuildValue(ctx.guild.id ,'currency_name')}{self.db.getGuildValue(ctx.guild.id ,'currency_emote')} Total supply")

    @commands.command()
    async def give(self, ctx, member, points):
        async with ctx.message.channel.typing():
            try:    
                payment = float(points)
            except ValueError:
                await ctx.channel.send(f":bank:: :no_entry: **The amount has to be an integer non-negative number**")
                return
            if payment<1:
                await ctx.channel.send(f":bank:: :no_entry: **The amount has to be an integer non-negative number**")
                return
            

            sender_amount= self.db.getPoints(ctx.guild.name, ctx.author.id)

            if sender_amount<payment:
                await ctx.channel.send(f":bank:: :x: **Insufficient amount**")
                return

            user = int(member.strip('<!@>'))
            member = await ctx.guild.fetch_member(user)


            self.db.transferPoints(ctx.guild.name, ctx.author.id, payment, member.id)


            await ctx.channel.send(f":bank:: :white_check_mark: {ctx.author.mention} gave **{payment}** {self.db.getGuildValue(ctx.guild.id ,'currency_name')}{self.db.getGuildValue(ctx.guild.id ,'currency_emote')} to {member.mention}")

    @give.error
    async def give_error(self, ctx, error):
        async with ctx.message.channel.typing():
            if isinstance(error, commands.MissingRequiredArgument):
                await ctx.message.reply(
                    embed=discord.Embed(
                        title=":bank:: :no_entry: An argument is missing",
                        description=f"Command syntax: `{self.db.getGuildValue(ctx.guild.id, 'prefix')}give [member] [coins]`",
                        color=discord.Color.red(),
                        )
                    )

    
    @commands.command()
    async def rain(self, ctx, donation, number_of_members):
        try:    
            donation = float(donation)
            number_of_members = int(number_of_members)
        except ValueError:
            await ctx.channel.send(f":bank:: :no_entry: **The amount has to be an integer non-negative number**")
            return
        
        if donation<1 or number_of_members<1:
            await ctx.channel.send(f":bank:: :no_entry: **The amount has to be an integer non-negative number**")
            return


        sender_amount= self.db.getPoints(ctx.guild.name, ctx.author.id)

        if sender_amount<donation:
            await ctx.channel.send(f":bank:: :x: **Insufficient amount**")
            return

        members = await ctx.guild.fetch_members(limit=150).flatten()
        members = list(filter(lambda x: x.bot is False and x.id!=ctx.author.id, members))

        if number_of_members > len(members):
            await ctx.channel.send(f":bank:: :x: **Τhere are not so many members in this server**")
            return

        donation_share = math.floor(donation/number_of_members) #calculate the amount each user gets
        
        #pick the winners
        winners = []
        for m in range(number_of_members):
            winner = random.choice(members)
            winners.append(winner)

        embed = discord.Embed(title = f":bank:: :white_check_mark: {ctx.author.name} made a rain :cloud_rain: of **{donation}** {self.db.getGuildValue(ctx.guild.id ,'currency_name')}{self.db.getGuildValue(ctx.guild.id ,'currency_emote')}",
                        color= ctx.author.color,
                        timestamp=datetime.utcnow())
        respond = ""


        self.db.setPoints(ctx.guild.name, ctx.author.id, sender_amount-donation) #decrease sender's points
        for winner in winners:
            recipient_amount= self.db.getPoints(ctx.guild.name, winner.id) 
            self.db.setPoints(ctx.guild.name, winner.id, recipient_amount+donation_share) #increase recipient's points
            respond += "\n"+ str(winner.mention ) + " got **" + str(donation_share) + f"** {self.db.getGuildValue(ctx.guild.id ,'currency_name')}{self.db.getGuildValue(ctx.guild.id ,'currency_emote')}"
        


        embed.add_field(name='Winners', 
                        value=respond,
                        inline=False
                        )
        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)
    
    @rain.error
    async def rain_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.reply(
                embed=discord.Embed(
                    title=":bank:: :no_entry: An argument is missing",
                    description=f"Command syntax: `{self.db.getGuildValue(ctx.guild.id, 'prefix')}rain [total_amount] [number of recipients]`",
                    color=discord.Color.red(),
                    )
                )

    @commands.command(aliases=['dr'])
    async def daily(self, ctx):

        reward_value = self.db.getGuildValue(ctx.guild.id, 'daily_reward')
        if reward_value == 0 :
            return

        lastclaim = self.db.getDailyRewardTime(ctx.guild.name, ctx.author.id)
        now = datetime.now()
        
        if (now - lastclaim) > timedelta(days=1):
            points = self.db.getPoints(ctx.guild.name, ctx.author.id)
            self.db.setPoints(ctx.guild.name, ctx.author.id, points+float(reward_value))
            self.db.setDailyRewardTime(ctx.guild.name, ctx.author.id, now)
            curr_name = self.db.getGuildValue(ctx.guild.id ,'currency_name')
            curr_emote = self.db.getGuildValue(ctx.guild.id ,'currency_emote')
            embed = discord.Embed(title = f":bank:: :white_check_mark: You clamed your daily reward!",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow())
            embed.add_field(name=f'{reward_value} {curr_name}{curr_emote}', value=f"Last claim was before {(now - lastclaim).days} days", inline=False)
            embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)

        else:
            d = (lastclaim+timedelta(days=1))-now
            seconds = d.total_seconds()
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60

            embed = discord.Embed(title = f":bank:: :x: You have already claimed your daily reward",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow())
            embed.add_field(name=':hourglass_flowing_sand: Next claim after', value=f"**{hours:.0f}** hours **{minutes:.0f}** minutes **{seconds:.0f}** seconds", inline=False)
            embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)


        await ctx.message.reply(embed=embed)



#===============RANDOM DROPS===================================================================================================
    async def spawn_reward(self, guild):
        curr_name = self.db.getGuildValue(guild.id ,'currency_name')
        curr_emote = self.db.getGuildValue(guild.id ,'currency_emote')
        async def reward_callback(interaction):
            try:
                reward = float(re.search(r'\d+', interaction.message.embeds[0].fields[0].name).group()) #get the reward points of the embed message
            except AttributeError:
                return
            except IndexError:
                return


            points = self.db.getPoints(interaction.message.guild.name, interaction.user.id)
            points += reward-1
            self.db.setPoints(interaction.message.guild.name, interaction.user.id, points)

            embed = discord.Embed(title = f"🎉 {interaction.user.name}  got the reward! 🎁",
                    color= interaction.user.color,
                    timestamp=datetime.utcnow())
            embed.add_field(name= "**" + self.reward_points[0] + f"** {curr_name}{curr_emote}" ,
                            value=f"{interaction.user.mention} got the random drop of **{reward}** {curr_name}{curr_emote} ",
                            inline=False
                            )
            embed.set_footer(text=f'Interaction by: {interaction.user.name}', icon_url=interaction.user.avatar_url)

            #del interaction.message.components[0]
            await interaction.edit_origin(content="", embed=embed, components=[])


        rewards = [
                    ['25', (205, 127, 50)],
                    ['250', (192, 192, 192)],
                    ['500', (255, 215, 0)]
                  ]
        self.reward_points = random.choices(population=rewards, weights=[0.9, 0.08, 0.02], k=1)[0]
        
        embed = discord.Embed(title = f"🎉 Its your lucky day, Get your reward! 🎁",
                color= discord.Color.from_rgb(self.reward_points[1][0], self.reward_points[1][1], self.reward_points[1][2]),
                timestamp=datetime.utcnow())
        embed.add_field(name= "**" + self.reward_points[0] + f"** {curr_name}{curr_emote}" ,
                        value="Press the 🎁 button below first to get them",
                        inline=False
                        )
        embed.set_footer(text=f'Requested by: {self.client.user.name}', icon_url=self.client.user.avatar_url)

        channel = random.choice(guild.text_channels)
        await channel.send(
            content=f"@everyone" , 
            embed=embed,
            components=[
                self.client.components_manager.add_callback(
                    Button(style=ButtonStyle.gray, label=f"Get {self.reward_points[0]} {curr_name}", id="reward", emoji="🎁"), reward_callback),
            ],
        )
            

    @tasks.loop(seconds=3600.0)
    async def reward(self):
        for guild in self.client.guilds:
            if self.db.getGuildValue(guild.id, 'drops'):
                if random.random() < 0.10:
                    await self.spawn_reward(guild)

    @reward.before_loop
    async def before_reward(self):
        await self.client.wait_until_ready()

#========= RANDOM DROPS =====================================================================================================================



            
def setup(client):
    client.add_cog(Economy(client))
