import discord
import logging
import math
import database
import pprint as debug
from datetime import datetime
from discord.ext import commands



logging.basicConfig(filename='Alwaysondude.log', level=logging.INFO, filemode='w', format='%(asctime)s:%(name)s:%(message)s', datefmt='%d %b %y %H:%M:%S')

class MyEvents(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.db = database.Database()


    @commands.Cog.listener()  
    async def on_ready(self):
        print(f'We have logged in as {self.client.user}')  # notification of login.

        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='my master to learn new things'))
    
        self.db.connect()
        for guild in self.client.guilds:
            self.db.insert('guilds', guild.id, guild.name, guild.chunked, guild.member_count, guild.owner_id)
            self.db.createTable(guild.name)
            for member in guild.members:
                self.db.insert(member.guild.name , member.id, member.name, member.discriminator, member.bot, member.nick, True, 0, member.guild.id)
        self.db.close_connection()
        print(f'Database update complete')        


    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.db.connect()
        self.db.insert(member.guild.name, member.id, member.name, member.discriminator, member.bot, member.nick, True, 0, member.guild.id)
        self.db.close_connection()

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        self.db.connect()
        self.db.delete(guild.name, member.id) #deletes the user from the guild's users table
        self.db.close_connection()


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        '''
        When the bot joins a new server\n
        Inserts the new guild in database\nCreates the table for the users and inserts the users
        '''
        self.db.connect()
        self.db.insert('guilds', guild.id, guild.name, guild.chunked, guild.member_count, guild.owner_id)
        self.db.createTable(guild.name)
        for member in guild.members:
            self.db.insert(guild.name, member.id, member.name, member.discriminator, member.bot, member.nick, True, 0, member.guild.id)
        self.db.close_connection()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        '''
        When the bot leaves a server\n
        The guilded deleted from the database
        '''
        self.db.connect()
        self.db.delete('guilds', guild.id)
        self.db.close_connection()


    @commands.Cog.listener()
    async def on_message(self, message):  # event that happens per any message.
        # each message has a bunch of attributes. Here are a few.
        # check out more by print(dir(message)) for example.
        logging.info(f"{message.guild.name}: {message.channel}: {message.author}: {message.author.name}: {message.content}")
        print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")
        if message.author.bot :
            return
        
        if not message.content.startswith('.'):
            self.db.connect()
            points = self.db.getPoints(message.guild.name, message.author.id)
            gained_points = math.floor(len(message.content)*0.12)
            points += gained_points
            self.db.setPoints(message.guild.name, message.author.id, points)
            print(f"{message.author} gained {gained_points} points")
            self.db.close_connection()


        if "hello" in message.content.lower():
            await message.channel.send(f"Hello {message.author.mention}, i am your digital friend {self.client.user.mention}, Do not panic i am peaceful. Mr. w0ch4 is my master!")

        if  "fuck" in message.content.lower():
            await message.channel.send(f"Go to hell {message.author.mention}")

    @commands.Cog.listener() 
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        self.db.connect()
        points = self.db.getPoints(user.guild.name, user.id)
        gained_points = 1
        self.db.setPoints(user.guild.name, user.id, points)
        print(f"{user} gained {gained_points} points")
        self.db.close_connection()

    '''
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"**:x: Command '{str(ctx.message.content).strip('.')}' is not found**")
    '''


def setup(client):
    client.add_cog(MyEvents(client))
