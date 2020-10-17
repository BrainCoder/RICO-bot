import discord
from discord.ext import commands
from discord.utils import get

client=commands.Bot(command_prefix='!')

def IsIn_CheckList():
    def inside_fn(ctx):
        #channelName = 760244981838512158
        if ctx.channel.id == 761118232161157152:
            return True
        return False
    return inside_fn

class DeveloperTools(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    #@client.command(checks=[IsIn_CheckList()])
    #@commands.has_any_role('Moderator', 'Developer')
    #async def cl(self, ctx,*,message):
    #    channel = self.client.get_channel(761759598419640341)
    #    await channel.send(f"<@{ctx.author.id}>: \n{message}")
    
    @client.command()
    @commands.has_any_role('Moderator', 'Developer')
    async def ping(self, ctx):
        await ctx.send(f'pong! Latency is {self.client.latency*1000}ms')
    
    @client.command()
    @commands.has_any_role('Moderator', 'Developer')
    async def GetChannel(self, ctx, id):
        channel = ctx.guild.get_channel(int(id))
        await ctx.send(f'{channel}')

def setup(client):
    client.add_cog(DeveloperTools(client))
