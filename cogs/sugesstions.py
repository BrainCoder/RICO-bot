import database

from discord.ext import commands
import settings
import utils

class welcome(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @commands.command(name="suggest")
    @commands.cooldown(2, 21600, commands.BucketType.user)
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
        settings.config["statusRoles"]["vip"],
        settings.config["statusRoles"]["boost-vip"],
        settings.config["statusRoles"]["member"])
    async def suggestion(self, ctx, *, suggestion):
        suggestions = self.client.get_channel(settings.config["channels"]["suggestions"])
        staff = self.client.get_channel(settings.config["channels"]["staff-lounge"])
        message = await suggestions.send(suggestion)
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        await staff.send(f'{ctx.author.name} suggested "{suggestion}"')


def setup(client):
    client.add_cog(welcome(client))