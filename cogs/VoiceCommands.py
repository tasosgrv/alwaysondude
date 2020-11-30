import discord
from datetime import datetime
import pprint as debug
from discord.ext import commands


class VoiceCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
    

    @commands.command()
    async def join(self, ctx):
        async with ctx.message.channel.typing():
            if ctx.author.voice is None:
                await ctx.send(f":x: **You have to be in a voice channel to use this command**")
            else:
                channel_id = ctx.author.voice.channel.id;
                channel = await self.client.fetch_channel(channel_id)
                self.voice = await channel.connect()
                await ctx.send(f"Connected to **{channel.name}**")


    @commands.command()
    async def leave(self, ctx):
        async with ctx.message.channel.typing():
            if not self.client.voice_clients:
                await ctx.send(f":x: **I am not connected to a channel**")
            else:
                requestor_guild = ctx.author.guild
                for voice_client in self.client.voice_clients:
                    if voice_client.guild == requestor_guild:
                        await voice_client.disconnect()
                        voice_client.cleanup()
                        await ctx.send(f"**Disconnected from the voice channel**")
    

def setup(client):
    client.add_cog(VoiceCommands(client))