import discord
import settings
import traceback
import sys
import asyncio

from discord import File
from discord.ext import commands
import utils
from sqlalchemy import insert, select

client = commands.Bot(command_prefix='!')


class DeveloperTools(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @client.command(name="checklist", aliases=['cl'])
    @commands.has_any_role(
        settings.config["statusRoles"]["moderator"],
        settings.config["statusRoles"]["developer"])
    async def cl(self, ctx, *, message):
        """Add the message to the dev team job-board"""
        channel = self.client.get_channel(settings.config["channels"]["job-board"])
        await channel.send(f"<@{ctx.author.id}>: \n{message}")
        await asyncio.sleep(5)
        await message.delete()

    @client.command(name="ping")
    async def ping(self, ctx):
        """Check the latency of the bot"""
        await ctx.send(f'pong! Latency is {self.client.latency * 1000}ms')

    @client.command(name="getchannel")
    @commands.has_any_role(
        settings.config["statusRoles"]["developer"])
    async def getchannel(self, ctx, id):
        """Find a channel with the channel ID"""
        channel = ctx.guild.get_channel(int(id))
        await ctx.send(f'{channel}')

    @commands.command(name='repeat', aliases=['mimic', 'copy'])
    @commands.has_any_role(
        settings.config["statusRoles"]["developer"])
    async def do_repeat(self, ctx, *, inp: str):
        """repeats the input you give it"""
        await ctx.send(inp)
    @do_repeat.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'inp':
                await ctx.send("You forgot to give me input to repeat!")

    @client.command()
    @commands.has_any_role(
        settings.config["statusRoles"]["developer"])
    async def verifyintegrityofdb(self, ctx):
        """Ensures that all users currently in the server are inside the database, and adds them if not."""
        new_entries = 0
        current_users = len(utils.conn.execute(utils.userdata.select()).fetchall())
        for user in ctx.guild.members:
            query = utils.userdata.select().where(utils.userdata.c.id == user.id)
            result = utils.conn.execute(query).fetchone()
            if not result and not user.bot:
                query = utils.userdata.insert(). \
                    values(id=user.id)
                utils.conn.execute(query)
                new_entries += 1
        new_count = len(utils.conn.execute(utils.userdata.select()).fetchall())
        await ctx.channel.send("The old amount of users was " + str(current_users) + \
                               "\nThe new amount of users is " + str(new_count))
    
    @commands.command()
    async def test(self, ctx):
        pass

def setup(client):
    client.add_cog(DeveloperTools(client))
