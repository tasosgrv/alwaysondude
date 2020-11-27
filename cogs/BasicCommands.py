import discord
from datetime import datetime
import pprint as debug
from discord.ext import commands

class BasicCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    
    @commands.command()
    async def ping(self, ctx):
        async with ctx.message.channel.typing(): #show tha the bot is typing
            await ctx.send(f"Ping: {round(self.client.latency*1000)} ms")

    

    @commands.command()
    async def history(self, ctx, member=None, limit=None):
        if member is None: member = ctx.author.mention
        counter = 0
        async for message in ctx.channel.history(limit=limit):
                counter +=1
        await ctx.send(f"{member} posted {counter} messages in this channel {ctx.channel.mention}")

    
    @commands.command()
    async def stats(self, ctx, member=None, limit=None):
        if member is None:
             member = ctx.author
        else:
            user = int(member.strip('<!@>'))
            member = await ctx.guild.fetch_member(user)
        embed = discord.Embed(title = f"Messege statistics for {member}",
                        color= member.color,
                        timestamp=datetime.utcnow())
        embed.set_thumbnail(url=member.avatar_url)
        #await ctx.send(f"{member.mention} posted: ")
        mentioned = 0
        total_messages = 0
        async with ctx.message.channel.typing():

            for channel in ctx.guild.channels:
                chan_perm = channel.permissions_for(member)
                mem_perm = member.permissions_in(channel)
                if channel.type.name == 'text' and member.permissions_in(channel).send_messages is True and ctx.author.permissions_in(channel).read_messages is True:
                    chan_messages_c=0
                    async for message in channel.history(limit=limit):
                        if member.mention in message.content:
                            mentioned+=1

                        if message.author.id==member.id:
                            chan_messages_c+=1
                            total_messages+=1
            
                    embed.add_field(name=f"{channel.name}", value=f"{str(chan_messages_c)} message(s)", inline=False)
                    #await ctx.send(f"{str(count)} messages in {channel.mention}")
            embed.add_field(name="In Summury", value= f"{str(total_messages)} total message(s) in the server \n{str(mentioned)} times your name mentioned", inline=False)
            embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
            #await ctx.send(f"{str(mentioned)} times your name mentioned")
            await ctx.send(embed=embed)
    
                        
    @commands.command(hidden=True)
    async def delete(self, ctx, member=None, limit=None):
        
        async with ctx.message.channel.typing():

            if member is None: member = ctx.author.mention
            count, messages = 0, []

            async for message in ctx.channel.history(limit=int(limit)):
                if message.author.mention == member.replace('!', ''):
                    messages.append(message)
                    count+=1
            
            deleted = await ctx.channel.delete_messages(messages)
            await ctx.channel.send(f'Deleted {str(count)} message(s) of {member} in this channel')


    @commands.command(hidden=True)
    async def clean(self, ctx, limit=None):
        async with ctx.message.channel.typing():
            deleted = await ctx.channel.purge(limit=int(limit))
            await ctx.channel.send(f'Deleted {len(deleted)} message(s)')
        


def setup(client):
    client.add_cog(BasicCommands(client))
