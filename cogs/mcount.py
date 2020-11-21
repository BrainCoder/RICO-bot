from discord.ext import commands, tasks

import settings

class SetReaction(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None
        self.mcount_update.start()

    @tasks.loop(minutes = 15)
    async def mcount_update(self):
        await self.client.wait_until_ready()
        guild = self.client.get_guild(settings.config["serverId"])
        mCount = guild.member_count
        channel = self.client.get_channel(settings.config["channels"]["memberscount"])
        print(f'There are now {mCount} members of this server')
        await channel.edit(name=(f'[{mCount} members]'))

def setup(client):
    client.add_cog(SetReaction(client))
