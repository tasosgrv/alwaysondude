import discord
from discord.ext import commands
from datetime import datetime
import re
import emoji


class adminCommands(commands.Cog):
    def __init__(self, client):
        self.client = client



    @commands.command(aliases=['pr'])
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, new_prefix=None):
        if new_prefix is None:
            await ctx.message.reply(
                embed=discord.Embed(
                    title=f":gear: The current prefix on **{ctx.guild.name}** is `{self.client.db.getGuildValue(ctx.guild.id, 'prefix')}`",
                    description=f"if you want to change it type `{self.client.db.getGuildValue(ctx.guild.id, 'prefix')}prefix [new_prefix]`",
                    color=discord.Color.red(),
                    )
                )
            return

        prefixes = ['.', '/', ',', '>', '!', '$']
        new_prefix = new_prefix.strip()
        if new_prefix not in prefixes:
            await ctx.message.reply(f":gear:: :no_entry: **Wrong entry**,\n The prefix is invalid\n Valid prefixes: `.` `,` `!` `/` `>` `$`")
            return        

        if self.client.db.setGuildValue(ctx.guild.id, 'prefix', new_prefix):
            await ctx.message.reply(f":gear:: ::white_check_mark: : The prefix for **{ctx.guild.name}** changed successfully to `{new_prefix}`")
        else:
            await ctx.message.reply(f":gear:: :no_entry: The command failed")



    @commands.command(aliases=['er'])
    @commands.has_permissions(administrator=True)
    async def earningrate(self, ctx, new_rate=None):
        
        if new_rate is None:
            await ctx.message.reply(f":gear: The current earning rate for **{self.client.db.getGuildValue(ctx.guild.id, 'currency_name')}** is **{self.client.db.getGuildValue(ctx.guild.id, 'earning_rate')}**")
            return

        try:
            new_rate = float(new_rate)
        except ValueError:
            await ctx.message.reply(f":gear:: :no_entry: **Wrong entry**,\nthe rate needs to be a number")
            return

        if new_rate<=1:
            await ctx.message.reply(f":gear:: :no_entry: **Wrong entry**,\nyou can't have a negative earning rate :D ")
            return


        if self.client.db.setGuildValue(ctx.guild.id, 'earning_rate', new_rate):
            await ctx.message.reply(f":gear:: ::white_check_mark: : The earning rate for **{ctx.guild.name}** changed successfully to **{new_rate}**")
        else:
            await ctx.message.reply(f":gear:: :no_entry: The command failed")

    @earningrate.error
    async def earningrate_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.reply(
                embed=discord.Embed(
                    title=":gear:: :no_entry: **An argument is missing**",
                    description=f"Command syntax: `{self.client.db.getGuildValue(ctx.guild.id, 'prefix')}earningrate [new reward]`",
                    color=discord.Color.red(),
                    )
                )

        if isinstance(error, commands.MissingPermissions):
            await ctx.message.reply(f":gear:: :no_entry_sign: **You are not allowed to run this command** ")


    @commands.command(aliases=['drps'])
    @commands.has_permissions(administrator=True)
    async def drops(self, ctx, new_state=None):

        if self.client.db.getGuildValue(ctx.guild.id, 'drops'):
            state = 'enabled'
        else:
            state = 'disabled'

        if new_state is None:
            await ctx.message.reply(f":gear: 🎁 The random drops are **{state}**. if you want to enable/disable them type .drops [enable/disable]")
            return

        if new_state == "enable":
            self.client.db.setGuildValue(ctx.guild.id, 'drops', 'True')
            await ctx.message.reply(f":gear: 🎁 :green_circle: The random drops are now **enabled**") 
        elif new_state == "disable":
            self.client.db.setGuildValue(ctx.guild.id, 'drops', 'False')
            await ctx.message.reply(f":gear: 🎁 :red_circle: The random drops are now **disabled**")
        else:
            await ctx.message.reply(f":gear: 🎁 :no_entry: **Wrong entry**,\n if you want to enable/disable the drops type {self.client.db.getGuildValue(ctx.guild.id, 'prefix')}drops [enable/disable]")



    @drops.error
    async def drops_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.reply(
                embed=discord.Embed(
                    title=":gear:: :no_entry: **An argument is missing**",
                    description=f"Command syntax: `{self.client.db.getGuildValue(ctx.guild.id, 'prefix')}drops [enable/disable]`",
                    color=discord.Color.red(),
                    )
                )

        if isinstance(error, commands.MissingPermissions):
            await ctx.message.reply(f":gear:: :no_entry_sign: **You are not allowed to run this command** ")
        



    @commands.command(aliases=['drw'])
    @commands.has_permissions(administrator=True)
    async def dailyreward(self, ctx, new_reward=None):
        
        if new_reward is None:
            await ctx.message.reply(f":gear: The current daily reward for {ctx.guild.name} is **{self.client.db.getGuildValue(ctx.guild.id, 'daily_reward')}** {self.client.db.getGuildValue(ctx.guild.id, 'currency_name')}:moneybag:")
            return

        try:
            new_reward = float(new_reward)
        except ValueError:
            await ctx.message.reply(f":gear:: :no_entry: **Wrong entry**,\nthe daily reward amount needs to be a number")
            return

        if new_reward<0:
            await ctx.message.reply(f":gear:: :no_entry: **Wrong entry**,\nyou can't have a negative earning rate :D ")
            return

        elif new_reward == 0:
            if self.client.db.setGuildValue(ctx.guild.id, 'daily_reward', new_reward):
                await ctx.message.reply(f":gear:: :no_entry: The daily rewards are now disabled")
            else:
                await ctx.message.reply(f":gear:: :no_entry: The command failed")

        else:
            if self.client.db.setGuildValue(ctx.guild.id, 'daily_reward', new_reward):
                await ctx.message.reply(f":gear:: ::white_check_mark: : The daily reward for **{ctx.guild.name}** changed successfully to **{new_reward}**{self.client.db.getGuildValue(ctx.guild.id, 'currency_name')}:moneybag:")
            else:
                await ctx.message.reply(f":gear:: :no_entry: The command failed")



    @dailyreward.error
    async def dailyreward_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.reply(
                embed=discord.Embed(
                    title=":gear:: :no_entry: An argument is missing",
                    description=f"Command syntax: `{self.client.db.getGuildValue(ctx.guild.id, 'prefix')}dailyreward [new reward]`",
                    color=discord.Color.red(),
                    )
                )

        if isinstance(error, commands.MissingPermissions):
            await ctx.message.reply(f":gear:: :no_entry_sign: **You are not allowed to run this command** ")


    @commands.command(aliases=['c'])
    @commands.has_permissions(administrator=True)
    async def currency(self, ctx, action=None, str_arg=None, points=None):

        if action is None:
            
            embed = discord.Embed(title=":gear: : :dollar: Currency Informations", color=ctx.author.color, timestamp=datetime.utcnow())
            embed.add_field(name="name", value=f"{self.client.db.getGuildValue(ctx.guild.id, 'currency_name')}", inline=False)
            embed.add_field(name="icon (emoji)", value=f"{self.client.db.getGuildValue(ctx.guild.id, 'currency_emote')}", inline=False)
            embed.add_field(name="Circulating Supply ", value=f"{self.client.db.getCirculatingSupply(ctx.guild.name)}", inline=False)
            embed.add_field(name="Total Supply", value=f"{self.client.db.getTotalSupply(ctx.guild.name)}", inline=False)
            embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
            await ctx.message.reply(embed=embed)
            return
        
        action = action.strip()

        if action=="add" or action=="remove":        
            try:
                user = int(str_arg.strip('<!@>'))           
            except ValueError: 
                await ctx.message.reply(f":gear:: :no_entry: **Invalid user**")
                return

            str_arg = await ctx.guild.fetch_member(user)

            try:    
                points = float(points)
            except ValueError:
                await ctx.message.reply(f":gear:: :no_entry: **The amount has to be an integer non-negative number**")
                return

            if points<1:
                await ctx.messsage.reply(f":gear:: :no_entry: **The amount has to be an integer non-negative number**")
                return

            sender_amount= self.client.db.getPoints(ctx.guild.name, self.client.user.id)
        
            if sender_amount<points:
                await ctx.message.reply(f":gear:: :x: **Insufficient amount**")
                return

            if action=="add":
                self.client.db.transferPoints(ctx.guild.name, self.client.user.id, points, str_arg.id)
                await ctx.message.reply(f":gear:: ::white_check_mark: : **{points}**{self.client.db.getGuildValue(ctx.guild.id, 'currency_emote')} added to {str_arg.mention}")
            else:
                self.client.db.transferPoints(ctx.guild.name, str_arg.id, points, self.client.user.id)
                await ctx.message.reply(f":gear:: ::white_check_mark: : **{points}**{self.client.db.getGuildValue(ctx.guild.id, 'currency_emote')} removed from {str_arg.mention}")
        
        elif action=="name":
            try:
                name = str(str_arg)
            except ValueError:
                await ctx.message.reply(f":gear:: :no_entry: **Invalid name**")
                return

            if self.client.db.setGuildValue(ctx.guild.id, 'currency_name', name):
                await ctx.message.reply(f":gear:: :white_check_mark: The currency name now changed to '{name}'")
            else:
                await ctx.message.reply(f":gear:: :no_entry: The currency name change failed")
            
        elif action=="emoji":

            try:
                name = str(str_arg)
            except ValueError:
                await ctx.message.reply(f":gear:: :no_entry: **Invalid input**")
                return
            # matches custom emote
            server_match = re.search(r'<a?:(\w+):(\d+)>', str_arg)
            # matches global emote
            custom_match = re.search(r'(:\w+:)', emoji.demojize(str_arg))

            if server_match:
                new_emoji = f"<:{server_match.group(1)}:{server_match.group(2)}>"
            elif custom_match:
                new_emoji = emoji.emojize(custom_match.group(1))
            else:
                await ctx.message.reply(f":gear:: :no_entry: Invalid emoji")
                return

            if self.db.setGuildValue(ctx.guild.id, 'currency_emote', new_emoji):
                await ctx.message.reply(f":gear:: :white_check_mark: The currency emoji now changed to '{new_emoji}'")
            else:
                await ctx.message.reply(f":gear:: :no_entry: The currency emoji change failed")

              
        else:
            embed=discord.Embed(title=":gear: : :no_entry: Action Not Found", description="Vallid Actions by exaples", color= ctx.author.color, timestamp=datetime.utcnow())
            embed.add_field(name="add ", value=f"`{self.client.db.getGuildValue(ctx.guild.id, 'prefix')}currency add @user 100`", inline=False)
            embed.add_field(name="remove", value=f"`{self.client.db.getGuildValue(ctx.guild.id, 'prefix')}currency remove @user 100`", inline=False)
            embed.add_field(name="name", value=f"`{self.client.db.getGuildValue(ctx.guild.id, 'prefix')}currency name coins`", inline=False)
            embed.add_field(name="emoji", value=f"`{self.client.db.getGuildValue(ctx.guild.id, 'prefix')}currency name 💲`", inline=False)
            embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
            await ctx.message.reply(embed=embed)

        return
        

    @currency.error
    async def currency_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.reply(
                embed=discord.Embed(
                    title=":gear:: :no_entry: An argument is missing",
                    description=f"Command syntax: `{self.client.db.getGuildValue(ctx.guild.id, 'prefix')}currency [add/remove] [member name] [points to transfer]`",
                    color=discord.Color.red(),
                    )
                )

def setup(client):
    client.add_cog(adminCommands(client))