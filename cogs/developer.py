import discord
import settings
import traceback
import sys

from discord import File
from discord.ext import commands
import utils
from sqlalchemy import insert, select
from utils import is_in_checklist_channel

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

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return
        ignored = (commands.CommandNotFound,)
        error = getattr(error, 'original', error)
        if isinstance(error, ignored):
            return
        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':
                await ctx.send('I could not find that member. Please try again.')
        elif isinstance(error, commands.CommandOnCooldown):
            message = await ctx.send(f'This command is on cooldown. Please wait {error.retry_after}s')
            await asyncio.sleep(5)
            await message.delete()
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

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
        await ctx.send(file = File('blacklist.txt'))



def setup(client):
    client.add_cog(DeveloperTools(client))
