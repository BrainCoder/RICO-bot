import utils
import database

from discord.ext import commands
from discord.ext.commands import Cog

import settings
import asyncio
import nest_asyncio


class Extra(commands.Cog):
    def __init__(self, client):
        nest_asyncio.apply()
        self.client = client
        self.afk_users = asyncio.run(self.build_afk_list())

    async def build_afk_list(self):
        afk_users = []
        rows = await database.userdata_select_query()
        for row in rows:
            if row[12] == 1:
                afk_users.append(row[0])
        return afk_users

    @commands.command(name="afk")
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
        settings.config["statusRoles"]["vip"],
        settings.config["statusRoles"]["boost-vip"],
        settings.config["statusRoles"]["member"],
    )
    async def afk(self, ctx, *, message: str = None):
        if message is not None:
            if "@everyone" in message or "@here" in message:
                return
            for word in message:
                if "@" in word:
                    return
        if ctx.author.id in self.afk_users:
            return
        nickname = 0
        if ctx.author.name != ctx.author.display_name:
            nickname = 1
        await database.userdata_update_query(ctx.author.id, {"afk": 1})
        await database.afk_event_insert(
            ctx.author.id, ctx.author.display_name, nickname, message
        )
        self.afk_users.append(ctx.author.id)
        if "[AFK]" not in ctx.author.display_name:
            try:
                await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}")
            except:
                await ctx.send("failed to change nickname")
        await utils.emoji(ctx)

    @Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return
        if self.afk_users is None:
            return
        if await utils.in_staff_channel(message.channel.id):
            return

        if message.author.id in self.afk_users and "!afk" not in message.content:
            await database.userdata_update_query(message.author.id, {"afk": 0})
            try:
                rows = await database.afk_event_select(message.author.id, True)
                if rows[4] == 1:
                    await message.author.edit(nick=rows[3])
                else:
                    await message.author.edit(nick=None)
            except:
                await message.channel.send("failed to change nickname")
            await database.afk_event_update(message.author.id)
            self.afk_users = await self.build_afk_list()
            await message.channel.send(
                f"{message.author.mention} you are no longer afk", delete_after=5
            )

        else:
            if len(message.mentions) > 0:
                for mention in message.mentions:
                    if mention.id in self.afk_users:
                        row = await database.afk_event_select(mention.id, True)
                        afk_message = row[2]
                        if afk_message is None:
                            await message.channel.send(f"{mention} is currently AFK")
                        else:
                            await message.channel.send(
                                f'{mention} is currently afk with the message "{afk_message}"'
                            )


def setup(client):
    client.add_cog(Extra(client))
