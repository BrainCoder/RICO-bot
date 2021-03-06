import discord
from discord.ext import commands, tasks

import settings
from itertools import cycle

status = cycle(['Version 2.1.13', 'DM me with complaints!'])


class background(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None
        self.mcount_update.start()
        self.activity_cycle.start()

    @tasks.loop(minutes=15)
    async def mcount_update(self):
        await self.client.wait_until_ready()
        guild = self.client.get_guild(settings.config["serverId"])
        mCount = guild.member_count
        channel = self.client.get_channel(settings.config["channels"]["memberscount"])
        print(f'There are now {mCount} members of this server')
        await channel.edit(name=(f'[{mCount} members]'))

    @tasks.loop(minutes=1)
    async def activity_cycle(self):
        await self.client.change_presence(status=discord.Status.online, activity=discord.Game(next(status)))


def setup(client):
    client.add_cog(background(client))
