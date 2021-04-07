import discord
from discord.ext import commands
from discord.ext.commands import Cog
import settings
import asyncio


class welcome(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._last_member = None
        self.suggestions = self.client.get_channel(
            settings.config["channels"]["suggestions"]
        )
        self.suggestion_logs = self.client.get_channel(
            settings.config["channels"]["suggestion-logs"]
        )
        self.blacklist = [
            "ban",
            "lemon",
            "@everyone",
            "@here",
        ]

    async def c_blacklist(self, query):
        for word in self.blacklist:
            if word in query:
                return True
        return False

    async def send_message(self, channel, suggestion):
        message = await channel.send(suggestion)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

    @commands.command(name="suggest", aliases=["suggestion"])
    @commands.cooldown(1, 21600, commands.BucketType.user)
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
        settings.config["statusRoles"]["vip"],
        settings.config["statusRoles"]["member"],
    )
    async def suggestion(self, ctx, *, suggestion=None):
        if suggestion is None:
            return
        if await self.c_blacklist(suggestion):
            return
        await self.send_message(self.suggestions, suggestion)
        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_author(name="Suggestion", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Author", value=ctx.author.mention, inline=False)
        embed.add_field(name="Suggestion", value=suggestion, inline=False)
        await self.suggestion_logs.send(embed=embed)
        await ctx.message.delete()

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == settings.config["botId"]:
            return
        if payload.channel_id == settings.config["channels"]["suggestions"]:
            channel = self.client.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if message.reactions[0].emoji == "💬":
                return
            yes = message.reactions[0].count
            nos = message.reactions[1].count
            if yes - nos >= 20:
                await self.passed_vote(message)
            if -15 >= yes - nos:
                await asyncio.sleep(5)
                await message.delete()

    async def passed_vote(self, message):
        await message.clear_reactions()
        await message.add_reaction("💬")
        channel = self.client.get_channel(settings.config["channels"]["poll-board"])
        await self.send_message(
            channel, f"__**Suggestion**__\n\n```{message.content}```"
        )


def setup(client):
    client.add_cog(welcome(client))
