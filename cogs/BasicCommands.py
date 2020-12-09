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

        if limit is not None:
            limit = int(limit)+1

        async with ctx.message.channel.typing():
            if member is None: 
                counter = 0
                async for message in ctx.channel.history(limit=limit):
                        counter +=1
                await ctx.send(f"{counter} message(s) in this channel {ctx.channel.mention}")
            else:

                user = int(member.strip('<!@>'))
                member = await ctx.guild.fetch_member(user)

                counter = 0
                async for message in ctx.channel.history(limit=limit):
                    if message.author == member:
                        counter +=1
                await ctx.send(f"{member.mention} sent {counter} message(s) in this channel {ctx.channel.mention}")


    
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
            
                    embed.add_field(name=f"{channel.name}", value=f"{str(chan_messages_c)} message(s)", inline=True)
                    #await ctx.send(f"{str(count)} messages in {channel.mention}")
            embed.add_field(name="In Summury", value= f"{str(total_messages)} total message(s) in the server \n{str(mentioned)} times your name mentioned", inline=True)
            embed.add_field(name="Joined at", value= f"{member.joined_at.strftime('%d/%m/%Y %H:%M')}", inline=False)
            embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar_url)
            #await ctx.send(f"{str(mentioned)} times your name mentioned")
            await ctx.send(embed=embed)
    
                        
    @commands.command(hidden=True)
    async def delete(self, ctx, member, limit=None):
        
        if limit is not None:
            limit = int(limit)+1

        async with ctx.message.channel.typing():

            if member is None:
                await ctx.channel.send(f"You have to specify a memeber after the commands")

            count, messages = 0, []

            async for message in ctx.channel.history(limit=limit):
                if message.author.mention == member.replace('!', ''):
                    messages.append(message)
                    count+=1
            
            deleted = await ctx.channel.delete_messages(messages)
            await ctx.channel.send(f'Deleted {str(count)} message(s) of {member} in this channel')


    @commands.command(hidden=True)
    async def clean(self, ctx, limit=None):

        self.request = ctx.message
        if limit is None:
            query = await ctx.channel.send(f"**:warning: Are you sure you want to delete all messages of this channel?**")
            await query.add_reaction("✅")
            await query.add_reaction("❌")
        else:
            await self.cleanall(ctx.channel, limit)

       
    async def cleanall(self, channel, limit):
        if limit is not None:
            limit = int(limit) + 1

        async with channel.typing():
            deleted = await channel.purge(limit=limit)
            await channel.send(f"Deleted {len(deleted)} message(s)")


    @commands.Cog.listener() 
    async def on_reaction_add(self, reaction, user):
        
        if self.request.author == user:
                
            channel = reaction.message.channel 
            if reaction.emoji=="✅" and int(reaction.count)>1:
                await self.cleanall(channel, limit=None)
            if reaction.emoji=="❌" and int(reaction.count)>1:
                await self.cleanall(channel, limit=1)
        
  

def setup(client):
    client.add_cog(BasicCommands(client))
