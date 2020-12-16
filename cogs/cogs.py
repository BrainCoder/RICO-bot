from discord.ext import commands

import settings
import traceback
import sys
import utils
from datetime import datetime

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
        log = f'{utils.timestr}`{extension}` {action}ed manually'
        prefix = settings.config["prefix"]
        if action == 'load':
            self.client.load_extension(f'cogs.{extension}')
            await ctx.message.add_reaction(emoji)
            if prefix == "!":
                await devlogs.send(log)
        elif action == 'unload':
            if extension == 'cogs':
                emoji = '❌'
                await ctx.message.add_reaction(emoji)
            else:
                self.client.unload_extension(f'cogs.{extension}')
                await ctx.message.add_reaction(emoji)
                if prefix == "!":
                    await devlogs.send(log)
        elif action == 'reload':
            self.client.unload_extension(f'cogs.{extension}')
            self.client.load_extension(f'cogs.{extension}')
            await ctx.message.add_reaction(emoji)
            if prefix == "!":
                await devlogs.send(log)
    @cog.error
    async def cog_handler(self, ctx, error):
        emoji = '❌'
        await ctx.message.add_reaction(emoji)
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(client):
    client.add_cog(cogs(client))
