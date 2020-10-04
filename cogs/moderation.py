import discord
from discord.ext import commands
from discord.utils import get

class ModCommands(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=0):
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount)
        await ctx.send("purged")

    @commands.command(pass_context=True)
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, user: discord.Member, role: discord.Role):
        await user.add_roles(role)
        await ctx.send(f"role added {role}")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.User = None, *, reason=None):
        if member == None or member == ctx.message.author:
            await ctx.channel.send("You cannot kick yourself")
            return
        if reason == None:
            reason = "For being a jerk!"
        message = f"https://tenor.com/view/get-out-gif-9615975"
        channel = self.client.get_channel(758576163630350366)
        await member.send(f"kicked for **{reason}** {message}" )
        await ctx.guild.kick(member, reason=reason)
        await channel.send(f"{member} has been kicked! for **{reason}** kicked by <@{ctx.author.id}>")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.User = None, *, reason=None):
        if member == None or member == ctx.message.author:
            await ctx.channel.send("You cannot Ban yourself")
            return
        if reason == None:
            reason = "For being a jerk!"
        message = f"https://tenor.com/view/get-out-gif-9615975"
        channel = self.client.get_channel(758576163630350366)
        userAvatarUrl = member.avatar_url
        await member.send(f"Banned for **{reason}** {message}" )
        await ctx.guild.ban(member, reason=reason)
        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        #await channel.send(f"{member} has been Banned! for **{reason}** banned by <@{ctx.author.id}>")
        embed.set_author(name="Ban", icon_url=userAvatarUrl)
        embed.add_field(name=f"{member} has been Banned! ", value=f"**for:** {reason} banned by: <@{ctx.author.id}>.")
        await channel.send(embed=embed)



    @commands.command()
    @commands.has_permissions(administrator=True)
    async def nuke(self, ctx, amount=100000):
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount)
        await ctx.send("chat nuked")



def setup(client):
    client.add_cog(ModCommands(client))
