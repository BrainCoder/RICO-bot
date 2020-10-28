import discord
import settings
import traceback
import sys
from discord.ext import commands


client=commands.Bot(command_prefix='!')

class DeveloperTools(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @client.command()
    @commands.has_any_role('Moderator', 'Developer')
    async def cl(self, ctx,*,message):
        channel = self.client.get_channel(settings.config["channels"]["job-board"]) #job-board
        await channel.send(f"<@{ctx.author.id}>: \n{message}")
    
    @client.command()
    @commands.has_any_role('Moderator', 'Developer')
    async def ping(self, ctx):
        await ctx.send(f'pong! Latency is {self.client.latency*1000}ms')
    
    @client.command()
    @commands.has_any_role('Moderator', 'Developer')
    async def GetChannel(self, ctx, id):
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
        ignored = (commands.CommandNotFound, )
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
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command(name='repeat', aliases=['mimic', 'copy'])
    @commands.has_any_role('Moderator', 'Developer')
    async def do_repeat(self, ctx, *, inp: str):
        await ctx.send(inp)

    @do_repeat.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'inp':
                await ctx.send("You forgot to give me input to repeat!")
    
    @client.command()
    async def test(self, ctx):
        for role in ctx.author.roles:
            if role.id != (763078830352891916):
                await ctx.send(f'This happened')
                return
        await ctx.send(f'That happened')

def setup(client):
    client.add_cog(DeveloperTools(client))
