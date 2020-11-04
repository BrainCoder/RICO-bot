import discord
from discord.ext import commands
from discord.ext.commands import Cog

from datetime import datetime
from better_profanity import profanity
from sqlalchemy import text, update
import settings
import utils
import asyncio
import re

whitelist= []
with open('whitelist.txt', 'r') as f:
    whitelist = [line.strip() for line in f]

profanity.load_censor_words_from_file('blacklist.txt', whitelist_words = whitelist)

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

#Devlogs setup
today = datetime.now()
ctoday = today.strftime("%d/%m/%Y")
ctime = today.strftime("%H:%M")
timestr = f'**[{ctoday}] [{ctime}] -**'
#Devlogs setup


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k] * float(v)
            except KeyError:
                raise commands.BadArgument("{} is an invalid time-key! h/m/s/d are valid!".format(k))
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        return time


class ModCommands(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @commands.command(name="purge", aliases=["clear"])
    @commands.has_any_role(
        settings.config["statusRoles"]["moderator"])
    async def purge(self, ctx, amount=5):
        """clears messages in the given channel"""
        if amount > 50:
            await ctx.send(f'You cannot purge more than 50 messages at a time')
        else:
            await ctx.message.delete()
            await ctx.channel.purge(limit=amount)

    @commands.command(name="nmember")
    @commands.has_any_role(
        settings.config["statusRoles"]["moderator"],
        settings.config["statusRoles"]["semi-moderator"])
    async def member(self, ctx, user: discord.Member):
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

    @commands.command(name="mute")
    @commands.has_any_role(
        settings.config["statusRoles"]["moderator"],
        settings.config["statusRoles"]["semi-moderator"])
    async def mute(self, ctx, user: discord.Member, *, reason=None):
        """mutes the user and puts a strike against their name"""
        await self.client.wait_until_ready()
        if reason == None:
            await ctx.channel.send('please give reason for mute')
        elif reason != None:
            channel = self.client.get_channel(settings.config["channels"]["log"])
            userAvatarUrl = user.avatar_url
            for discord.guild in self.client.guilds:
                Mute_role = user.guild.get_role(settings.config["statusRoles"]["muted"])
            await user.send(
                f"Muted for '{reason}' by <@{ctx.author.id}>\nTo resolve this mute please communicate with the memeber of staff who muted you")
            await user.add_roles(Mute_role)
            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
            embed.set_author(name="Mute", icon_url=userAvatarUrl)
            embed.add_field(name=f"{user} has been Muted! ", value=f"**for:** {reason} Muted by: <@{ctx.author.id}>.")
            await channel.send(embed=embed)

    @commands.command(name="cooldown")
    @commands.has_any_role(
        settings.config["statusRoles"]["moderator"],
        settings.config["statusRoles"]["semi-moderator"])
    async def cooldown(self, ctx, user: discord.Member, *, time: TimeConverter = None):
        """takes the user out of the general channel for a specific amount of time"""
        cooldown_role = user.guild.get_role(settings.config["statusRoles"]["cooldown"])
        logs_channel = self.client.get_channel(settings.config["channels"]["log"])
        userAvatarUrl = user.avatar_url
        if time:
            await user.add_roles(cooldown_role)
            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
            embed.set_author(name="user", icon_url=userAvatarUrl)
            embed.add_field(name=f'{user} cooled-down by {ctx.author}',
                            value=f'The cooldown will be removed in {time}s, or a moderator will have to remove it manually')
            await logs_channel.send(embed=embed)
            await asyncio.sleep(time)
            await user.remove_roles(cooldown_role)
            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
            embed.set_author(name="user", icon_url=userAvatarUrl)
            embed.add_field(name=f'{user} is no longer cooled-down',
                            value=f'The cooldown was removed automatically by the bot')
            await logs_channel.send(embed=embed)
        else:
            await ctx.send(f'Please give a timer for the cooldown')

    @commands.command(name="nunmute")
    @commands.has_any_role(
        settings.config["statusRoles"]["moderator"],
                           settings.config["statusRoles"]["semi-moderator"])
    async def nunmute(self, ctx, user: discord.Member, *, time: TimeConverter = None):
        """unmute the user"""
        await self.client.wait_until_ready()
        muted = False
        self_muted = False
        self_mute_role = ctx.guild.get_role(settings.config["statusRoles"]["self-mute"])
        muted_role = ctx.guild.get_role(settings.config["statusRoles"]["muted"])
        channel = self.client.get_channel(settings.config["channels"]["log"])
        userAvatarUrl = user.avatar_url
        if time:
            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
            embed.set_author(name="Unmute", icon_url=userAvatarUrl)
            embed.add_field(name=f"{user} will be unmuted in {time}s! ", value=f"Unmuted by: <@{ctx.author.id}>.")
            await channel.send(embed=embed)
            await asyncio.sleep(time)
        if muted_role in user.roles:
            await user.remove_roles(muted_role)
            muted = True
        if self_mute_role in user.roles:
            await user.remove_roles(self_mute_role)
            self_muted = True
        if muted or self_muted:
            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
            embed.set_author(name="Unmute", icon_url=userAvatarUrl)
            embed.add_field(name=f"{user} has been Unmuted! ", value=f"Unmuted by: <@{ctx.author.id}>.")
            await channel.send(embed=embed)
            if not self_muted:
                unmute_query = utils.mod_event.insert(). \
                    values(recipient_id=user.id, event_type=4, event_time=utils.datetime.now(),
                           issuer_id=ctx.author.id, historical=0)
                utils.conn.execute(unmute_query)
                prior_mute_queries = text(f'update mod_event set historical = 1 where recipient_id = {user.id} '
                                          f'and event_type = 3 and historical = 0')
                utils.conn.execute(prior_mute_queries)

    @commands.command(name="kick")
    @commands.has_any_role(
        settings.config["statusRoles"]["moderator"])
    async def kick(self, ctx, member: discord.User = None, *, reason=None):
        """kicks the user from the server"""
        if member == None or member == ctx.message.author:
            await ctx.channel.send("You cannot kick yourself")
            return
        if reason == None:
            reason = "For being a jerk!"
        message = f"https://tenor.com/view/get-out-gif-9615975"
        channel = self.client.get_channel(settings.config["channels"]["log"])  # log
        await member.send(f"kicked for **{reason}**\n{message}")
        await ctx.guild.kick(member, reason=reason)
        userAvatarUrl = member.avatar_url
        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_author(name="Kick", icon_url=userAvatarUrl)
        embed.add_field(name=f"{member} has been Kicked! ", value=f"**for:** {reason} Kicked by: <@{ctx.author.id}>.")
        await channel.send(embed=embed)

    @commands.command(name="ban")
    @commands.has_any_role(
        settings.config["statusRoles"]["moderator"])
    async def ban(self, ctx, member: discord.User = None, *, reason=None):
        """bans the user from the server"""
        if member == None or member == ctx.message.author:
            await ctx.channel.send("You cannot Ban yourself")
            return
        if reason == None:
            reason = "For being a jerk!"
        message = f"https://tenor.com/view/bane-no-banned-and-you-are-explode-gif-16047504"
        channel = self.client.get_channel(settings.config["channels"]["log"])  # log
        userAvatarUrl = member.avatar_url
        await member.send(f"Banned for **{reason}**\n{message}")
        await ctx.guild.ban(member, reason=reason)
        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_author(name="Ban", icon_url=userAvatarUrl)
        embed.add_field(name=f"{member} has been Banned! ", value=f"**for:** {reason} banned by: <@{ctx.author.id}>.")
        await channel.send(embed=embed)

    @commands.command(name="automod")
    @commands.has_any_role(
        settings.config["statusRoles"]["moderator"])
    async def automod_edit(self, ctx, arg=None, *words):
        invarg = 'please clarify if you are adding or removing a word. Type `!automod add {word}` to add the word, or `!automod remove {word}` to remove the word'
        if arg == None:
            await ctx.send(invarg)
        elif arg == 'add':
            with open('blacklist.txt', "a", encoding="utf-8") as f:
                f.write("".join([f"{w}\n" for w in words]))
            emoji = '✅'
            await ctx.message.add_reaction(emoji)
            profanity.load_censor_words_from_file('blacklist.txt', whitelist_words = whitelist)
            await devlogs.send(f'{timestr}Reloaded `blacklist.txt` and `whitelist.txt` due to edit')
        elif arg == 'remove':
            with open('blacklist.txt', "r", encoding="utf-8") as f:
                stored = [w.strip() for w in f.readlines()]
            with open('blacklist.txt', "w", encoding="utf-8") as f:
                f.write("".join([f"{w}\n" for w in stored if w not in words]))
                profanity.load_censor_words_from_file('blacklist.txt', whitelist_words = whitelist)
                await devlogs.send(f'{timestr}Reloaded `blacklist.txt` and `whitelist.txt` due to edit')
            emoji = '✅'
            await ctx.message.add_reaction(emoji)
        else:
            await ctx.send(invarg)

    @Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            if profanity.contains_profanity(message.content):
                await message.delete()

    @commands.command()
    @commands.has_any_role(
        settings.config["statusRoles"]["member"],
        settings.config["statusRoles"]["moderator"],
        settings.config["statusRoles"]["semi-moderator"])
    async def lynch(self, ctx, member: discord.Member):
        if ctx.author == member:
            await ctx.channel.send("You can't lynch yourself!")
            return
        query = utils.userdata.select().where(utils.userdata.c.id == member.id)
        result = utils.conn.execute(query).fetchone()
        if result:
            current_lynches = result[5] + 1
            if utils.datetime.now() > (utils.datetime.fromtimestamp(result[7]) + utils.timedelta(hours=8)):
                current_lynches = 1
                make_historical_query = text(f'update mod_event set historical = 1 '
                                             f'where recipient_id = {member.id} and event_type = 6')
                utils.conn.execute(make_historical_query)
            successful_lynches = result[6]
            if current_lynches >= 3:
                await ctx.channel.send(f'{member.mention} has been lynched')
                query = update(utils.userdata).where(utils.userdata.c.id == member.id) \
                    .values(lynch_count=0, successful_lynch_count=successful_lynches + 1, lynch_expiration_time=0)
                utils.conn.execute(query)
                lynch_role = ctx.guild.get_role(settings.config["statusRoles"]["muted"])
                await member.add_roles(lynch_role)
                mod_query = utils.mod_event.insert(). \
                    values(recipient_id=member.id, event_type=6, event_time=utils.datetime.now(),
                           issuer_id=ctx.author.id, historical=0)
                utils.conn.execute(mod_query)
                find_lynches_query = text(f'select issuer_id from mod_event where recipient_id = {member.id} '
                                          f'and historical = 0')
                lynchers = utils.conn.execute(find_lynches_query)
                lyncher_list = ""
                for lyncher in lynchers:
                    lyncher_list += self.client.get_user(lyncher[0]).mention + " "
                channel = self.client.get_channel(settings.config["channels"]["log"])  # log
                await channel.send(f'User {member} was lynched by: {lyncher_list}')
            else:
                await ctx.channel.send(f'lynch acknowledged')
                query = update(utils.userdata).where(utils.userdata.c.id == member.id) \
                    .values(lynch_count=current_lynches,
                            lynch_expiration_time=(utils.datetime.now() + utils.timedelta(hours=8)).timestamp())
                utils.conn.execute(query)
                mod_query = utils.mod_event.insert(). \
                    values(recipient_id=member.id, event_type=6, event_time=utils.datetime.now(),
                           issuer_id=ctx.author.id, historical=0)
                utils.conn.execute(mod_query)
            member_role = ctx.guild.get_role(settings.config["statusRoles"]["member"])
            await ctx.author.remove_roles(member_role)


def setup(client):
    client.add_cog(ModCommands(client))
