import discord
from discord.ext import commands
import sys
import traceback
import asyncio
import re
import settings

client=commands.Bot(command_prefix='!')

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h":3600, "s":1, "m":60, "d":86400}

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k]*float(v)
            except KeyError:
                raise commands.BadArgument("{} is an invalid time-key! h/m/s/d are valid!".format(k))
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))

class Extra(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    
    #@commands.command()
    #@commands.has_any_role('Member')
    #async def SelfMute(self, ctx, time:TimeConverter = None):
    #    user = ctx.author
    #    channel = self.client.get_channel(settings.config["channels"]["log"])
    #    for discord.guild in self.client.guilds:
    #        Selfmute_Role = user.guild.get_role(settings.config["statusRoles"]["selfmute"])
    #    await user.add_roles(Selfmute_Role)
    #    await channel.send(("Muted {} for {}s" if time else "Muted {}").format(user, time))
    #    if time:
    #        await asyncio.sleep(time)
    #        await user.remove_roles(Selfmute_Role)

    @client.command()
    async def DoSomething(self, ctx):
        await ctx.channel.send("*Does your mum*")

    @client.command()
    async def habibi(self, ctx):
        await ctx.message.delete()
        await ctx.channel.send("""
                \\
            \\
             <:despair:568237870288994315>     Pass the habibi down
           /
        /
        """
        )

    @client.command()
    @commands.has_any_role('💎 VIP', '💎 Booster VIP', 'Moderator', 'Semi-Moderator')
    async def UI(self, ctx, *, member: discord.Member = None):
        DateCreated = member.created_at.strftime("%A, %B %d %Y at %H:%M:%S %p")

        MemberJoinedAt = member.joined_at.strftime("%A, %B %d %Y at %H:%M:%S %p")
        userAvatarUrl = member.avatar_url

        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)

        embed.set_author(name="UI", icon_url=userAvatarUrl)
        embed.add_field(name='Account was created at: ', value=f"{DateCreated}.")
        embed.add_field(name="Member joined at: ", value=f"{MemberJoinedAt}.")
        await ctx.send(embed=embed)

    @client.command()
    @commands.has_any_role('💎 VIP', '💎 Booster VIP', 'Moderator', 'Semi-Moderator')
    async def avatar(self, ctx, *, avamember: discord.Member = None):
        userAvatarUrl = avamember.avatar_url
        await ctx.send(f"{avamember}'s avatar is: {userAvatarUrl}")

def setup(client):
    client.add_cog(Extra(client))
