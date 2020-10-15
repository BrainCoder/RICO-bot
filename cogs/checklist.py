from discord.ext import commands
import settings
client=commands.Bot(command_prefix='!')

def IsIn_CheckList():
    def inside_fn(ctx):
        #channelName = 760244981838512158
        if ctx.channel.id == settings.config["channels"]["checklist"]: #staff stuff check-list
            return True
        return False
    return inside_fn

class checklist(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @client.command(checks=[IsIn_CheckList()])
    async def cl(self, ctx,*,message):
        channel = self.client.get_channel(761759598419640341) #I don't know what channel this is
        await channel.send(f"<@{ctx.author.id}>: \n{message}")

def setup(client):
    client.add_cog(checklist(client))
