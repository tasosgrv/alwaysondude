import discord
from discord.ext import commands
import database


class adminCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.db = database.Database()

    @commands.command(aliases=['er'])
    @commands.has_permissions(administrator=True)
    async def earningrate(self, ctx, new_rate):
        
        try:
            new_rate = float(new_rate)
        except ValueError:
            await ctx.message.reply(f":gear:: :no_entry: **Wrong entry**,\nthe rate needs to be a number")
            return

        if new_rate<-1:
            await ctx.message.reply(f":gear:: :no_entry: **Wrong entry**,\nyou can't have a negative earning rate :D ")
            return


        ###TODO Database interaction code 
        # 
        #

        await ctx.message.reply(f":gear:: ::white_check_mark: : The earning rate for **{ctx.guild.name}** changed successfully to **{new_rate}**")

    @earningrate.error
    async def earningrate_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.reply(f":gear:: :no_entry: **An argument is missing** \nCommand syntax: .earningrate [new rate]")

        if isinstance(error, commands.MissingPermissions):
            await ctx.message.reply(f":gear:: :no_entry_sign: **You are not allowed to run this command** ")


    @commands.command(aliases=['c'])
    @commands.has_permissions(administrator=True)
    async def currency(self, ctx, action, member, points):
        action = action.strip()
        if not (action=="add" or action=="remove"):
            await ctx.message.reply(f":gear:: :no_entry: **Action not found**\nCommand syntax; .currency [add/remove] [member name] [points to transfer]")
            return

        try:
            user = int(member.strip('<!@>'))           
        except ValueError: 
            await ctx.message.reply(f":gear:: :no_entry: **Invalid user**")
            return

        member = await ctx.guild.fetch_member(user)

        try:    
            points = float(points)
        except ValueError:
            await ctx.message.reply(f":gear:: :no_entry: **The amount has to be an integer non-negative number**")
            return

        if points<1:
            await ctx.messsage.reply(f":gear:: :no_entry: **The amount has to be an integer non-negative number**")
            return

        sender_amount= self.db.getPoints(ctx.guild.name, self.client.user.id)
    
        if sender_amount<points:
            await ctx.message.reply(f":gear:: :x: **Insufficient amount**")
            return

        if action=="add":
            self.db.transferPoints(ctx.guild.name, self.client.user.id, points, member.id)
            await ctx.message.reply(f":gear:: ::white_check_mark: : **{points}**:moneybag: added to {member.mention}")
        else:
            self.db.transferPoints(ctx.guild.name, member.id, points, self.client.user.id)
            await ctx.message.reply(f":gear:: ::white_check_mark: : **{points}**:moneybag: removed from {member.mention}")

        

    @currency.error
    async def currency_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.reply(f":gear:: :no_entry: **An argument is missing** \nCommand syntax: .currency [add/remove] [member name] [points to transfer]")

        if isinstance(error, commands.MissingPermissions):
            await ctx.message.reply(f":gear:: :no_entry_sign: **You are not allowed to run this command** ")

def setup(client):
    client.add_cog(adminCommands(client))