import discord
import logging
import math
import database
import pprint as debug
from datetime import datetime
from discord.ext import commands



logging.basicConfig(filename='./logs/Alwaysondude.log', level=logging.INFO, filemode='w', format='%(asctime)s:%(name)s:%(message)s', datefmt='%d %b %y %H:%M:%S')

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
                if member.name == self.client.user.name:
                   self.db.insert(member.guild.name , member.id, member.name, member.discriminator, member.bot, member.nick, True, 5000, member.guild.id) 
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
            if member.name == self.client.name:
                self.db.insert(member.guild.name , member.id, member.name, member.discriminator, member.bot, member.nick, True, 5000, member.guild.id) 
            self.db.insert(guild.name, member.id, member.name, member.discriminator, member.bot, member.nick, True, 10, member.guild.id)
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
        
        if not message.content.startswith('.') and len(message.content)<211:
            self.db.connect()
            points = self.db.getPoints(message.guild.name, message.author.id)
            gained_points = math.floor(len(message.content)*0.12)
            points += gained_points
            self.db.setPoints(message.guild.name, message.author.id, points)
            self.db.close_connection()
            if gained_points>0:
                print(f"{message.guild.name}: {message.author} gained {gained_points} points")
                logging.info(f"{message.guild.name}: {message.author} gained {gained_points} points")


        if "hello" in message.content.lower():
            await message.channel.send(f"Hello {message.author.mention}, i am your digital friend {self.client.user.mention}, Do not panic i am peaceful. Mr. w0ch4 is my master!")

        if  "fuck" in message.content.lower():
            await message.channel.send(f"Go to hell {message.author.mention}")

    @commands.Cog.listener() 
    async def on_reaction_add(self, reaction, user):
        if user.bot  or reaction.message.author==self.client.user: #if the reaction made from a bot or if the reaction made to the client
            return
        self.db.connect()
        points = self.db.getPoints(user.guild.name, user.id)
        gained_points = 1
        self.db.setPoints(user.guild.name, user.id, points+gained_points)
        self.db.close_connection()
        print(f"{user.guild.name}: {user} gained {gained_points} points")
        logging.info(f"{user.guild.name}: {user} gained {gained_points} points")

    @commands.Cog.listener() 
    async def on_reaction_remove(self, reaction, user):
        if user.bot or reaction.message.author==self.client.user:
            return
        self.db.connect()
        points = self.db.getPoints(user.guild.name, user.id)
        remove_points = 1
        self.db.setPoints(user.guild.name, user.id, points-remove_points)
        self.db.close_connection()
        print(f"{user.guild.name}: {user} lost {remove_points} points")
        logging.info(f"{user.guild.name}: {user} lost {remove_points} points")

    '''
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"**:x: Command '{str(ctx.message.content).strip('.')}' is not found**")
    '''


def setup(client):
    client.add_cog(MyEvents(client))
