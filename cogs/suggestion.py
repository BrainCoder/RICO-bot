import discord
from discord.ext import commands
from discord.ext.commands import Cog
import settings


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
        if "@everyone" in suggestion or "@here" in suggestion:
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
        # Check if it was a bot who added the reaction
        if payload.user_id == settings.config["botId"]:
            return

        # Check that it is in the suggestions channel
        if payload.channel_id == settings.config["channels"]["suggestions"]:

            # Isolates the message as a variable
            channel = self.client.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            # Check if passed vote
            if message.reactions[0].emoji == "💬":
                return

            # Isolate how many yes's it has
            yes = message.reactions[0].count

            # Isolate how many no's it has
            nos = message.reactions[1].count

            # Calc how many total votes it has
            if yes - nos >= 20:
                await self.passed_vote(message)
            if yes - nos >= -15:
                await asyncio.sleep(5)
                await message.delete()

    async def passed_vote(self, message):

        # Remove reactions from message
        await message.clear_reactions()

        # Add reactions
        await message.add_reaction("💬")

        # Send message to poll board
        channel = self.client.get_channel(settings.config["channels"]["poll-board"])
        mod_ping = message.guild.get_role(settings.config["staffRoles"]["mod-ping"])
        await self.send_message(
            channel, f"__**Suggestion**__\n\n```{message.content}```{mod_ping.mention}"
        )


def setup(client):
    client.add_cog(welcome(client))
