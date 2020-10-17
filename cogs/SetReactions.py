from discord.ext import commands

client=commands.Bot(command_prefix='!')



class SetReaction(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None




def setup(client):
    client.add_cog(SetReaction(client))
