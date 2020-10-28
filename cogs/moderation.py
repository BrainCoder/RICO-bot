import discord
from discord.ext import commands
import settings
import sys
import traceback
import asyncio
import re

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
        return time

class ModCommands(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @commands.command()
    @commands.has_any_role('Moderator')
    async def purge(self, ctx, amount=5):
        if amount > 50:
            await ctx.send(f'You cannot purge more than 50 messages at a time')
        else:
            await ctx.message.delete()
            await ctx.channel.purge(limit=amount)

    @commands.command()
    @commands.has_any_role('Moderator', 'Semi-Moderator')
    async def Nmember (self, ctx, user: discord.Member):
        await self.client.wait_until_ready()
        channel = self.client.get_channel(settings.config["channels"]["log"])
        userAvatarUrl = user.avatar_url
        for discord.guild in self.client.guilds:
            Member_role = user.guild.get_role(settings.config["statusRoles"]["member"])
        await user.add_roles(Member_role)
        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_author(name="Member", icon_url=userAvatarUrl)
        embed.add_field(name=f"{user} has been given member! ", value=f"Member given by: <@{ctx.author.id}>.")
        await channel.send(embed=embed)

    @commands.command()
    @commands.has_any_role('Moderator', 'Semi-Moderator')
    async def mute (self, ctx, user: discord.Member, *,reason=None):
        await self.client.wait_until_ready()
        if reason == None:
            await ctx.channel.send('please give reason for mute')
        elif reason != None:
            channel = self.client.get_channel(settings.config["channels"]["log"])
            userAvatarUrl = user.avatar_url
            for discord.guild in self.client.guilds:
                Mute_role = user.guild.get_role(settings.config["statusRoles"]["muted"])
            await user.send(f"Muted for '{reason}' by <@{ctx.author.id}>\nTo resolve this mute please communicate with the memeber of staff who muted you")
            await user.add_roles(Mute_role)
            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
            embed.set_author(name="Mute", icon_url=userAvatarUrl)
            embed.add_field(name=f"{user} has been Muted! ", value=f"**for:** {reason} Muted by: <@{ctx.author.id}>.")
            await channel.send(embed=embed)





    @commands.command()
    @commands.has_any_role('Moderator', 'Semi-Moderator')
    async def unmute (self, ctx, user: discord.Member, *, time:TimeConverter = None):
        await self.client.wait_until_ready()
        Unmute_Role = user.guild.get_role(settings.config["statusRoles"]["muted"])
        channel = self.client.get_channel(settings.config["channels"]["log"])
        userAvatarUrl = user.avatar_url
        if time:
            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
            embed.set_author(name="Unmute", icon_url=userAvatarUrl)
            embed.add_field(name=f"{user} will be unmuted in {time}s! ", value=f"Unmuted by: <@{ctx.author.id}>.")
            await channel.send(embed=embed)
            await asyncio.sleep(time)
        await user.remove_roles(Unmute_Role)
        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_author(name="Unmute", icon_url=userAvatarUrl)
        embed.add_field(name=f"{user} has been Unmuted! ", value=f"Unmuted by: <@{ctx.author.id}>.")
        await channel.send(embed=embed)








    @commands.command()
    @commands.has_any_role('Moderator')
    async def kick(self, ctx, member: discord.User = None, *, reason=None):
        if member == None or member == ctx.message.author:
            await ctx.channel.send("You cannot kick yourself")
            return
        if reason == None:
            reason = "For being a jerk!"
        message = f"https://tenor.com/view/get-out-gif-9615975"
        channel = self.client.get_channel(settings.config["channels"]["log"])#log
        await member.send(f"kicked for **{reason}**\n{message}" )
        await ctx.guild.kick(member, reason=reason)
        userAvatarUrl = member.avatar_url
        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_author(name="Kick", icon_url=userAvatarUrl)
        embed.add_field(name=f"{member} has been Kicked! ", value=f"**for:** {reason} Kicked by: <@{ctx.author.id}>.")
        await channel.send(embed=embed)

    @commands.command()
    @commands.has_any_role('Moderator')
    async def ban(self, ctx, member: discord.User = None, *, reason=None):
        if member == None or member == ctx.message.author:
            await ctx.channel.send("You cannot Ban yourself")
            return
        if reason == None:
            reason = "For being a jerk!"
        message = f"https://tenor.com/view/bane-no-banned-and-you-are-explode-gif-16047504"
        channel = self.client.get_channel(settings.config["channels"]["log"])#log
        userAvatarUrl = member.avatar_url
        await member.send(f"Banned for **{reason}**\n{message}" )
        await ctx.guild.ban(member, reason=reason)
        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_author(name="Ban", icon_url=userAvatarUrl)
        embed.add_field(name=f"{member} has been Banned! ", value=f"**for:** {reason} banned by: <@{ctx.author.id}>.")
        await channel.send(embed=embed)

def setup(client):
    client.add_cog(ModCommands(client))
