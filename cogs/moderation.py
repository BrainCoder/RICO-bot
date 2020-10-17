import discord
from discord.ext import commands
import settings
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
    @commands.has_permissions(manage_roles=True)
    async def mute (self, ctx, user: discord.Member, *,reason=None):
        await self.client.wait_until_ready()
        if reason == None:
            await ctx.channel.send('please give reason for mute')
        elif reason != None:
            author = ctx.message.author
            channel = self.client.get_channel(758576163630350366) #I don't know what channel this is
            userAvatarUrl = user.avatar_url
            for discord.guild in self.client.guilds:
                Mute_role = user.guild.get_role(762405273599869018) #I don't know what role this is
                Mute_role = user.guild.get_role(settings.config["statusRoles"]["muted"])
            #await member.send(f"Muted for '{reason}' by {author}\nTo resolve this mute please communicate with the memeber of staff who muted you")
            await user.add_roles(Mute_role)
            #await req(guild_id, user_id, role.id, reason=reason)
            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
            #await channel.send(f"{user} has been Muted! for **{reason}** Muted by <@{ctx.author.id}>")
            embed.set_author(name="Mute", icon_url=userAvatarUrl)
            embed.add_field(name=f"{user} has been Muted! ", value=f"**for:** {reason} Muted by: <@{ctx.author.id}>.")
            await channel.send(embed=embed)


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute (self, ctx, user: discord.Member):
        await self.client.wait_until_ready()
        for discord.guild in self.client.guilds:
            Unmute_Role = user.guild.get_role(762405273599869018) #I don't know what role this is
            channel = self.client.get_channel(758576163630350366) #I don't know what channel this is

            Unmute_Role = user.guild.get_role(settings.config["statusRoles"]["muted"])
        channel = self.client.get_channel(settings.config["channels"]["log"])#log
        await user.remove_roles(Unmute_Role)
        userAvatarUrl = user.avatar_url
        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        #await channel.send(f"{member} has been Banned! for **{reason}** banned by <@{ctx.author.id}>")
        embed.set_author(name="UnMute", icon_url=userAvatarUrl)
        embed.add_field(name=f"{user} has been Unmuted! ", value=f"Unmuted by: <@{ctx.author.id}>.")
        await channel.send(embed=embed)


    @commands.command()
    @commands.has_permissions(kick_members=True)
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
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.User = None, *, reason=None):
        if member == None or member == ctx.message.author:
            await ctx.channel.send("You cannot Ban yourself")
            return
        if reason == None:
            reason = "For being a jerk!"
        message = f"https://tenor.com/view/get-out-gif-9615975"
        channel = self.client.get_channel(settings.config["channels"]["log"])#log
        userAvatarUrl = member.avatar_url
        await member.send(f"Banned for **{reason}**\n{message}" )
        await ctx.guild.ban(member, reason=reason)
        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        #await channel.send(f"{member} has been Banned! for **{reason}** banned by <@{ctx.author.id}>")
        embed.set_author(name="Ban", icon_url=userAvatarUrl)
        embed.add_field(name=f"{member} has been Banned! ", value=f"**for:** {reason} banned by: <@{ctx.author.id}>.")
        await channel.send(embed=embed)

def setup(client):
    client.add_cog(ModCommands(client))
