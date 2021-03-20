import discord
from discord.ext import commands
from discord.ext.commands import Cog

from datetime import datetime
import settings
import utils


class welcome(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._last_member = None
        self.del_logs = self.client.get_channel(
            settings.config["channels"]["deleted-logs"]
        )

    @Cog.listener()
    async def on_message_delete(self, message):
        embed = discord.Embed(
            color=0x00DCFF,
            timestamp=datetime.utcnow(),
            description=f"Message deleted in <#{message.channel.id}>",
        )
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        embed.add_field(name="Content", value=message.content, inline=False)
        embed.add_field(
            name="ID",
            value=f"```python\nUser = {message.author.id}\nMessage = {message.id}```",
            inline=False,
        )
        embed.add_field(name="Date", value=message.created_at, inline=False)
        await self.del_logs.send(embed=embed)


def setup(client):
    client.add_cog(welcome(client))
