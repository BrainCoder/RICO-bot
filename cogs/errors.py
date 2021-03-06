import utils

import discord
from discord.ext import commands
import traceback
import sys


class ErrorHandler(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

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
            better_time = await utils.convert_from_seconds(error.retry_after)
            await ctx.send(content=f'This command is on cooldown. Please wait {better_time}', delete_after=5)
        elif isinstance(error, commands.MissingAnyRole):
            pass
        elif isinstance(error, discord.Forbidden):
            pass
        elif isinstance(error, discord.NotFound):
            pass
        else:
            print('\n--------', file=sys.stderr)
            print(f'Time      : {utils.timestr}', file=sys.stderr)
            print(f'Command   : {ctx.command}', file=sys.stderr)
            print(f'Message   : {ctx.message.content}', file=sys.stderr)
            print(f'Author    : {ctx.author}', file=sys.stderr)
            print(" ", file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(client):
    client.add_cog(ErrorHandler(client))
