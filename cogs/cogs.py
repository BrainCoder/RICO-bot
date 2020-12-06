from discord.ext import commands

import settings
import traceback
import sys
from datetime import datetime

today = datetime.now()
ctoday = today.strftime("%d/%m/%Y")
ctime = today.strftime("%H:%M")
timestr = f'**[{ctoday}] [{ctime}] - **'

class cogs(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @commands.command(name="cog", aliases=["cogs"])
    @commands.has_any_role(
        settings.config["statusRoles"]["developer"])
    async def cog(self, ctx, action, extension):
        """Command to manually toggle cogs. For action use either\n**load** - load the cog\n**unload** - unload the cog\n**reload** - reload the cog"""
        devlogs = self.client.get_channel(settings.config["channels"]["devlog"])
        emoji = '✅'
        log = f'{timestr}`{extension}` {action}ed manually'
        if action == 'load':
            self.client.load_extension(f'cogs.{extension}')
            await ctx.message.add_reaction(emoji)
            await devlogs.send(log)
        elif action == 'unload':
            if extension == 'cogs':
                emoji = '❌'
                await ctx.message.add_reaction(emoji)
            else:
                self.client.unload_extension(f'cogs.{extension}')
                await ctx.message.add_reaction(emoji)
                await devlogs.send(log)
        elif action == 'reload':
            self.client.unload_extension(f'cogs.{extension}')
            self.client.load_extension(f'cogs.{extension}')
            await ctx.message.add_reaction(emoji)
            await devlogs.send(log)
    @cog.error
    async def cog_handler(self, ctx, error):
        emoji = '❌'
        if isinstance(error, commands.ExtensionNotLoaded):
            await ctx.message.add_reaction(emoji)
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.message.add_reaction(emoji)
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(client):
    client.add_cog(cogs(client))
