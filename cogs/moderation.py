import discord
from discord.ext import commands
from discord.utils import get

client=commands.Bot(command_prefix='!')
class moderations(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None



    @commands.command()
    async def ping(self, ctx):
        await ctx.send('fuck!')
        print ('test')



def setup(client):
    client.add_cog(moderations(client))
