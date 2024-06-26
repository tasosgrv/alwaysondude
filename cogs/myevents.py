import discord
import logging
import math
import pprint as debug
from datetime import datetime
from discord.ext import tasks, commands



logging.basicConfig(filename='./logs/Alwaysondude.log', level=logging.INFO, filemode='w', format='%(asctime)s:%(name)s:%(message)s', datefmt='%d %b %y %H:%M:%S')

class MyEvents(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.chpresence.start()


    @commands.Cog.listener()  
    async def on_ready(self):
        print(f'We have logged in as {self.client.user}')  # notification of login.

        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f'your bets 💰 in {len(self.client.guilds)} servers'))
        
        for guild in self.client.guilds:
            self.client.db.insert('guilds', guild.id, guild.name, guild.chunked, guild.member_count, guild.owner_id)
            self.client.db.createTable(guild.name)
            for member in guild.members:
                if member.id == self.client.user.id:
                   self.client.db.insert(member.guild.name , member.id, member.name, member.discriminator, member.bot, member.nick, True, 5000, member.guild.id, "2000-01-01 00:00:00.00") 
                self.client.db.insert(member.guild.name , member.id, member.name, member.discriminator, member.bot, member.nick, True, 0, member.guild.id, "2000-01-01 00:00:00.00")
    
        print(f'Database update complete')   



    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.client.db.insert(member.guild.name, member.id, member.name, member.discriminator, member.bot, member.nick, True, 0, member.guild.id, "2000-01-01 00:00:00.00")


    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        self.client.db.delete(guild.name, member.id) #deletes the user from the guild's users table


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        '''
        When the bot joins a new server\n
        Inserts the new guild in database\nCreates the table for the users and inserts the users
        '''

        self.client.db.insert('guilds', guild.id, guild.name, guild.chunked, guild.member_count, guild.owner_id)
        self.client.db.createTable(guild.name)
        for member in guild.members:
            if member.id == self.client.user.id:
                self.client.db.insert(member.guild.name, member.id, member.name, member.discriminator, member.bot, member.nick, True, 5000, member.guild.id, "2000-01-01 00:00:00") 
            self.client.db.insert(guild.name, member.id, member.name, member.discriminator, member.bot, member.nick, True, 10, member.guild.id, "2000-01-01 00:00:00")

        print(f"Joined in {guild.name}")
        logging.info(f"Joined in {guild.name}")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        '''
        When the bot leaves a server\n
        The guild deleted from the database
        '''

        self.client.db.delete('guilds', guild.id)
        self.client.db.dropTable(guild.name)

        print(f"{guild.name} removed me ")
        logging.info(f"{guild.name} removed me ")



    @commands.Cog.listener()
    async def on_message(self, message):  # event that happens per any message.
        # each message has a bunch of attributes. Here are a few.
        # check out more by print(dir(message)) for example.

        '''
        logging.info(f"{message.guild.name}: {message.channel}: {message.author}: {message.author.name}: {message.content}")
        print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")
        '''
        if message.author.bot: # if the message was sent from any bot
            return
        
        if not message.guild: #if a user send a private message to the bot
            await message.reply("Use this bot only on Servers")
            return

        if message.content == self.client.user.mention:
            await message.channel.send(f"Hello {message.author.mention} i am {self.client.user.mention} your casino bot, my commands prefix is `{self.client.db.getGuildValue(message.guild.id, 'prefix')}` use `{self.client.db.getGuildValue(message.guild.id, 'prefix')}help` to see what can i do!")
        
        if not message.content.startswith(self.client.db.getGuildValue(message.guild.id, 'prefix')) and len(message.content)<211:

            points = self.client.db.getPoints(message.guild.name, message.author.id)
            gained_points = len(message.content)*float(self.client.db.getGuildValue(message.guild.id, 'earning_rate'))
            points += gained_points

            if gained_points>1:
                self.client.db.setPoints(message.guild.name, message.author.id, points)
            
                print(f"{message.guild.name}: {message.author} gained {gained_points} points")
                logging.info(f"{message.guild.name}: {message.author} gained {gained_points} points")
            
            

        if "hello" in message.content.lower():
            await message.channel.send(f"Hello {message.author.mention}, i am your digital friend {self.client.user.mention}, Do not panic i am peaceful. Mr. w0ch4 is my master!")

        if  "fuck" in message.content.lower():
            await message.channel.send(f"Go to hell {message.author.mention}")


    @commands.Cog.listener() 
    async def on_reaction_add(self, reaction, user):
        if user.bot or reaction.message.author==self.client.user: #if the reaction made from a bot or if the reaction made to the client
            return
        points = self.client.db.getPoints(user.guild.name, user.id)
        gained_points = 1
        self.client.db.setPoints(user.guild.name, user.id, points+gained_points)
        print(f"{user.guild.name}: {user} gained {gained_points} points")
        logging.info(f"{user.guild.name}: {user} gained {gained_points} points")

    @commands.Cog.listener() 
    async def on_reaction_remove(self, reaction, user):
        if user.bot or reaction.message.author==self.client.user:
            return

        points = self.client.db.getPoints(user.guild.name, user.id)
        remove_points = 1
        self.client.db.setPoints(user.guild.name, user.id, points-remove_points)
        print(f"{user.guild.name}: {user} lost {remove_points} points")
        logging.info(f"{user.guild.name}: {user} lost {remove_points} points")

    
    
    @tasks.loop(seconds=1800.0)
    async def chpresence(self):
        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f'your bets 💰 in {len(self.client.guilds)} servers'))

    @chpresence.before_loop
    async def before_chpresence(self):
        await self.client.wait_until_ready()


    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            await ctx.message.reply(
                embed=discord.Embed(
                    title=f":x: Command not found",
                    description=f"Command **'{str(ctx.message.content).strip('.')}'** is not found",
                    color=discord.Color.red(),
                    )
                )
        if isinstance(error, commands.MissingPermissions):
            await ctx.message.reply(
                embed=discord.Embed(
                    title=":gear:: :no_entry_sign: You are not allowed to run this command",
                    description="You have to be an administrator on this server to use this command",
                    color=discord.Color.red(),
                    )
                )



def setup(client):
    client.add_cog(MyEvents(client))
