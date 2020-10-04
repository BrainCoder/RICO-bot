import discord
from discord.ext import commands
from discord.utils import get

client=commands.Bot(command_prefix='!')



class Checklist(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    def is_in_channel3():
        def inside_fn(ctx):
            #channelName = 760244981838512158
            if ctx.channel.id == 761118232161157152:
                return True
            return False
        return inside_fn

    @client.command(checks=[is_in_channel3()])
    async def cl(ctx,*,message):
        channel = client.get_channel(761759598419640341)#job board
        await channel.send(f"<@{ctx.author.id}>: \n{message}")

def setup(client):
    client.add_cog(checklist(client))
