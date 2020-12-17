import settings
import utils

from discord.ext import commands


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
        log = f'{utils.timestr}`{extension}` {action}ed manually'
        prefix = settings.config["prefix"]
        if action == 'load':
            self.client.load_extension(f'cogs.{extension}')
            await utils.emoji(ctx, '✅')
            if prefix == "!":
                await devlogs.send(log)
        elif action == 'unload':
            if extension == 'cogs':
                await utils.emoji(ctx, '❌')
            else:
                self.client.unload_extension(f'cogs.{extension}')
                await utils.emoji(ctx, '✅')
                if prefix == "!":
                    await devlogs.send(log)
        elif action == 'reload':
            self.client.unload_extension(f'cogs.{extension}')
            self.client.load_extension(f'cogs.{extension}')
            await utils.emoji(ctx, '✅')
            if prefix == "!":
                await devlogs.send(log)
    @cog.error
    async def cog_handler(self, ctx, error):
        await utils.emoji(ctx, '❌')
        await utils.dotraceback(ctx, error)

def setup(client):
    client.add_cog(cogs(client))
