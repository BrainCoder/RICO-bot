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
        channel = self.client.get_channel(557201575270154241)#logs
        await member.send(f"kicked for **{reason}**\n{message}" )
        await ctx.guild.kick(member, reason=reason)
        userAvatarUrl = member.avatar_url
        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_author(name="Kick", icon_url=userAvatarUrl)
        embed.add_field(name=f"{member} has been Kicked! ", value=f"**for:** {reason} Kicked by: <@{ctx.author.id}>.")
        await channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.User = None, *, reason=None):
        if member == None or member == ctx.message.author:
            await ctx.channel.send("You cannot Ban yourself")
            return
        if reason == None:
            reason = "For being a jerk!"
        message = f"https://tenor.com/view/get-out-gif-9615975"
        channel = self.client.get_channel(557201575270154241)
        userAvatarUrl = member.avatar_url
        await member.send(f"Banned for **{reason}**\n{message}" )
        await ctx.guild.ban(member, reason=reason)
        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        #await channel.send(f"{member} has been Banned! for **{reason}** banned by <@{ctx.author.id}>")
        embed.set_author(name="Ban", icon_url=userAvatarUrl)
        embed.add_field(name=f"{member} has been Banned! ", value=f"**for:** {reason} banned by: <@{ctx.author.id}>.")
        await channel.send(embed=embed)

    @commands.command()
    @commands.has_any_role('Moderator')
    async def mute (self, ctx, member: discord.User, *,reason=None):
        if reason == None:
            await ctx.channel.send('please give reason for mute')
        author = ctx.message.author
        channel = self.client.get_channel(557201575270154241)
        userAvatarUrl = member.avatar_url
        await member.send(f"Muted for '{reason}' by {author}\nTo resolve this mute please communicate with the memeber of staff who muted you")
        await discord.guild.Member.add_roles(520288471399792670)
        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        #await channel.send(f"{member} has been Banned! for **{reason}** banned by <@{ctx.author.id}>")
        embed.set_author(name="Mute", icon_url=userAvatarUrl)
        embed.add_field(name=f"{member} has been Muted! ", value=f"**for:** {reason} Muted by: <@{ctx.author.id}>.")
        await channel.send(embed=embed)



def setup(client):
    client.add_cog(ModCommands(client))
