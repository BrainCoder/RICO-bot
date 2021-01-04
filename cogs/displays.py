import discord
import settings
import utils
from discord.ext import commands


class SetReaction(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @commands.command(name='displays')
    @commands.has_any_role(
        settings.config["staffRoles"]["developer"])
    async def displays(self, ctx, display):
        await ctx.message.delete()
        if display is None:
            pass
        elif display == "rules":
            await self.BuildRulesEmbed(ctx)
        elif display == "welcome":
            await self.welcome(ctx)

    async def BuildRulesEmbed(self, ctx):
        embed = discord.Embed(title="Rules", url="https://tenor.com/view/idiot-lafuddyduddy-rules-follow-the-rules-penguin-gif-16685859", color=0x00dcff)
        embed.set_author(name="NoPorn", url="https://discord.gg/CFR9bt", icon_url="https://cdn.discordapp.com/icons/519330541720436736/a_2bdbaecdd90c85cdc8e9108d8a8c5907.png?size=128")
        rules = await utils.extract_data('resources/rules.txt')
        for rule in rules:
            embed.add_field(name=f'Rule {rules.index(rule)+1}', value=rule, inline=False)
        embed.set_footer(text="NoPorn Companion was made by the NoPorn development team, please DM the bot for more information")
        await ctx.send(embed=embed)

    async def welcome(self, ctx):
        await self.BuildWelcomeEmbed(ctx)
        await self.BuildChannelsEmbed(ctx)
        await self.BuildMiscEmbed(ctx)

    async def BuildWelcomeEmbed(self, ctx):
        embed = discord.Embed(title="Welcome", url="https://www.youtube.com/watch?v=dTS2Yya9Jj4&list=LLhv0ss-9EZsbjxEU67Rawsg&index=38", color=0x00dcff)
        embed.set_author(name="NoPorn", url="https://discord.gg/CFR9bt", icon_url="https://cdn.discordapp.com/icons/519330541720436736/a_2bdbaecdd90c85cdc8e9108d8a8c5907.png?size=128")
        embed.add_field(name="Backround info", value=f"\
            This server was created with the purpose of helping people overcome their drive to watch porn. We have a bot to keep track of the number of days you've\
            been clean, learn more about this in <#{settings.config['channels']['streak-guide']}> where you can also assign yourself the mode that you're attempting, and to see the commands that you can apply there.", inline=False)
        embed.add_field(name="Server Creation Date", value="9/12/2018")
        embed.set_footer(text="NoPorn Companion was made by the NoPorn development team, please DM the bot for more information")
        await ctx.send(embed=embed)

    async def BuildChannelsEmbed(self, ctx):
        helper = ctx.guild.get_role(settings.config['otherRoles']['helper'])
        embed = discord.Embed(title="Channels", url="https://www.youtube.com/watch?v=0itU7sA765U", color=0x00faa8)
        embed.set_author(name="NoPorn", url="https://discord.gg/CFR9bt", icon_url="https://cdn.discordapp.com/icons/519330541720436736/a_2bdbaecdd90c85cdc8e9108d8a8c5907.png?size=128")
        embed.add_field(name="Channels", value=f"\
            <#{settings.config['channels']['emergency']}>: Urgent help if you might PMO. You can ping a {helper.mention} if you need to talk to someone. \n\
            <#{settings.config['channels']['tips-and-reasons']}>: Reasons and methods to stop watching porn. \n\
            <#{settings.config['channels']['daily-updates']}>: Posts about how your day went. \n\
            <#{settings.config['channels']['streak-guide']}>: A guide for how to interact with the bot. \n\
            <#{settings.config['channels']['roles']}>: To get roles")
        embed.set_footer(text="NoPorn Companion was made by the NoPorn development team, please DM the bot for more information")
        await ctx.send(embed=embed)

    async def BuildMiscEmbed(self, ctx):
        embed = discord.Embed(title="Other Info", url="https://tenor.com/view/give-you-alittle-bit-more-info-abit-more-info-little-bit-info-information-info-gif-15208503", color=0x00faa8)
        embed.set_author(name="NoPorn", url="https://discord.gg/CFR9bt", icon_url="https://cdn.discordapp.com/icons/519330541720436736/a_2bdbaecdd90c85cdc8e9108d8a8c5907.png?size=128")
        embed.add_field(name="Complaints", value=f"Send a direct message to <@{settings.config['botId']}> with your complaints if you have any. In order to do this, you need to have your DM's open")
        embed.set_footer(text="NoPorn Companion was made by the NoPorn development team, please DM the bot for more information")
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(SetReaction(client))
