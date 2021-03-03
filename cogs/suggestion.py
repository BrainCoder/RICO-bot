import discord
from discord.ext import commands
import settings


class welcome(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @commands.command(name="suggest", aliases=['suggestion'])
    @commands.cooldown(1, 21600, commands.BucketType.user)
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
        settings.config["statusRoles"]["vip"],
        settings.config["statusRoles"]["member"])
    async def suggestion(self, ctx, *, suggestion=None):
        suggestions = self.client.get_channel(settings.config["channels"]["suggestions"])
        suggestion_logs = self.client.get_channel(settings.config["channels"]["suggestion-logs"])

        if '@everyone' in suggestion or '@here' in suggestion:
            return
        if suggestion is None:
            return

        message = await suggestions.send(suggestion)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_author(name="Suggestion", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Author", value=ctx.author.mention, inline=False)
        embed.add_field(name="Suggestion", value=suggestion, inline=False)
        await suggestion_logs.send(embed=embed)

        await ctx.message.delete()


def setup(client):
    client.add_cog(welcome(client))
