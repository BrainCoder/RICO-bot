import discord
from discord.ext import commands
from discord.ext.commands import cooldown

import random
import aiohttp
import settings


class Extra(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @commands.command(name="8ball", aliases=['8b'])
    @cooldown(1, 60)
    async def _8ball(self, ctx, *, question):
        """standard 8ball command"""
        responses = [
            'It is certain',
            'It is decidedly so',
            'Yes Definatley',
            'You may rely on it',
            'As I se it, yes',
            'Most Likely',
            'Outlook good',
            'Yes.',
            'Signs point to yes',
            'Reply hazy, try again',
            'Ask again later',
            'Better not tell you now',
            'Cannot predict now',
            'Concentrate and ask again',
            'Dont count on it',
            'My reply is no',
            'My sources say no',
            'Outlook not so good',
            'Very doubtful'
        ]
        if '@everyone' in question or '@here' in question:
            emoji = '❌'
            await ctx.message.add_reaction(emoji)
        else:
            await ctx.send(f' **Question:** {question}\n**Answer:** {random.choice(responses)}')

    @commands.command(name="dosomething")
    async def dosomething(self, ctx):
        """try it and find out ;)"""
        await ctx.channel.send("*Does your mum*")

    @commands.command(name="userinfo", aliases=["ui"])
    @commands.has_any_role(
        settings.config["statusRoles"]["vip"],
        settings.config["statusRoles"]["boost-vip"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"])
    async def ui(self, ctx, *, member: discord.Member = None):
        # this definatley can be tidied in the future
        """gives basic info on the user tagged in the arg"""
        if member is None:
            DateCreated = ctx.author.created_at.strftime("%A, %B %d %Y at %H:%M:%S %p")
            MemberJoinedAt = ctx.author.joined_at.strftime("%A, %B %d %Y at %H:%M:%S %p")
            userAvatarUrl = ctx.author.avatar_url
            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
            embed.set_author(name="UI", icon_url=userAvatarUrl)
            embed.add_field(name='Account was created at: ', value=f"{DateCreated}.")
            embed.add_field(name="Member joined at: ", value=f"{MemberJoinedAt}.")
            await ctx.send(embed=embed)
        else:
            DateCreated = member.created_at.strftime("%A, %B %d %Y at %H:%M:%S %p")
            MemberJoinedAt = member.joined_at.strftime("%A, %B %d %Y at %H:%M:%S %p")
            userAvatarUrl = member.avatar_url
            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
            embed.set_author(name="UI", icon_url=userAvatarUrl)
            embed.add_field(name='Account was created at: ', value=f"{DateCreated}.")
            embed.add_field(name="Member joined at: ", value=f"{MemberJoinedAt}.")
            await ctx.send(embed=embed)

    @commands.command(name="avatar", aliases=["av"])
    @commands.has_any_role(
        settings.config["statusRoles"]["vip"],
        settings.config["statusRoles"]["boost-vip"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"])
    async def avatar(self, ctx, *, avamember: discord.Member = None):
        """sends a link of the users avatar"""
        if avamember is None:
            userAvatarUrl = ctx.author.avatar_url
            await ctx.send(f'<@{ctx.author.id}>s avatar is:\n{userAvatarUrl}')
        else:
            userAvatarUrl = avamember.avatar_url
            await ctx.send(f"<@{avamember.id}>s avatar is:\n{userAvatarUrl}")

    @commands.command(name="gfsandwich")
    async def gfsandwich(self, ctx):
        """Evidence that the bot is hounds gf"""
        Hound = False
        HDev = ctx.guild.get_role(settings.config["staffRoles"]["head-dev"])
        for role in ctx.author.roles:
            if role.id == HDev.id:
                Hound = True
        if not Hound:
            await ctx.send('Ur not my dad :c')
        else:
            await ctx.send('uwu what kinda of sandwich does daddy want =^.^=', delete_after=5)

    @commands.command(name="emergency", aliases=['m'])
    async def emergency(self, ctx):
        """Gets an emergency link from emergency.nofap.com website."""
        url = "https://emergency.nofap.com/director.php?cat=em&religious=false"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as response:
                link_decoded = (await response.read()).decode()
                await ctx.send(link_decoded)


def setup(client):
    client.add_cog(Extra(client))
