import discord
import settings
from discord.ext import commands


async def rules(ctx):
    embed = discord.Embed(title="Rules", url="https://tenor.com/view/idiot-lafuddyduddy-rules-follow-the-rules-penguin-gif-16685859", color=0x00dcff)
    embed.set_author(name="NoPorn", url="https://discord.gg/CFR9bt", icon_url="https://cdn.discordapp.com/icons/519330541720436736/a_2bdbaecdd90c85cdc8e9108d8a8c5907.png?size=128")
    embed.add_field(name="Rule 1", value="\
        Do not post sexually suggestive (includes fetishes that are suggestive for some people) or gore containing pictures, \
        videos or links to them. Skin showing, or tight clothes, from the knees to the shoulders for women and from the knees \
        to the navel for men are considered sexually suggestive.", inline=False)
    embed.add_field(name="Rule 2", value="Do not have a sexually suggestive profile picture, name, or status.", inline=False)
    embed.add_field(name="Rule 3", value="Do not say sexually suggestive things when not asking for help or simp after someone.", inline=False)
    embed.add_field(name="Rule 4", value="Do not troll members while they're seeking help.", inline=False)
    embed.add_field(name="Rule 5", value="Do not search for images with the bot by using words that could lead to another users relapse, or are borderline sexual.", inline=False)
    embed.add_field(name="Rule 6", value="Do not spam pings, media, messages or ping moderators without a good reason.", inline=False)
    embed.add_field(name="Rule 7", value="Do not post invite links without the consent of an admin or moderator.", inline=False)
    embed.add_field(name="Rule 8", value="Do not behave in a toxic way towards, bully, or harass other members, or insult religions.", inline=False)
    embed.add_field(name="Rule 9", value="Do not use profanity with the intent of insulting in any of the core channels.", inline=False)
    embed.add_field(name="Rule 10", value="Do not complain excessively about others.", inline=False)
    embed.add_field(name="Rule 11", value="Do not disrespect staff members for a moderation decision. Comply and if you really think what happened was unjust then direct message the bot a complaint.", inline=False)
    embed.add_field(name="Rule 12", value="Do not take the wrong gender role.", inline=False)
    embed.add_field(name="Rule 13", value="Any action undertaken by a member of this server that can be viewed as hostile/inflammatory to another server is neither encouraged nor allowed.", inline=False)
    embed.add_field(name="Rule 14", value="Do not violate the Discord terms of service. (https://discordapp.com/terms)", inline=False)
    embed.set_footer(text="NoPorn Companion was made by the NoPorn development team, please DM the bot for more information")
    await ctx.send(embed=embed)

async def welcome(ctx):
    await wembed(ctx)
    await cembed(ctx)
    await oembed(ctx)

async def wembed(ctx):
    embed = discord.Embed(title="Welcome", url="https://www.youtube.com/watch?v=dTS2Yya9Jj4&list=LLhv0ss-9EZsbjxEU67Rawsg&index=38", color=0x00dcff)
    embed.set_author(name="NoPorn", url="https://discord.gg/CFR9bt", icon_url="https://cdn.discordapp.com/icons/519330541720436736/a_2bdbaecdd90c85cdc8e9108d8a8c5907.png?size=128")
    embed.add_field(name="Backround info", value=f"\
        This server was created with the purpose of helping people overcome their drive to watch porn. We have a bot to keep track of the number of days you've\
        been clean, learn more about this in <#{settings.config['channels']['streak-guide']}> where you can also assign yourself the mode that you're attempting, and to see the commands that you can apply there.", inline=False)
    embed.add_field(name="Server Creation Date", value="9/12/2018")
    embed.set_footer(text="NoPorn Companion was made by the NoPorn development team, please DM the bot for more information")
    await ctx.send(embed=embed)

async def cembed(ctx):
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

async def oembed(ctx):
    embed = discord.Embed(title="Other Info", url="https://tenor.com/view/give-you-alittle-bit-more-info-abit-more-info-little-bit-info-information-info-gif-15208503", color=0x00faa8)
    embed.set_author(name="NoPorn", url="https://discord.gg/CFR9bt", icon_url="https://cdn.discordapp.com/icons/519330541720436736/a_2bdbaecdd90c85cdc8e9108d8a8c5907.png?size=128")
    embed.add_field(name="Complaints", value=f"Send a direct message to <@{settings.config['botId']}> with your complaints if you have any. In order to do this, you need to have your DM's open")
    embed.set_footer(text="NoPorn Companion was made by the NoPorn development team, please DM the bot for more information")
    await ctx.send(embed=embed)


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
            await rules(ctx)
        elif display == "welcome":
            await welcome(ctx)


def setup(client):
    client.add_cog(SetReaction(client))
