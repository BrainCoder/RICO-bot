import utils
import database

import discord
from discord import File
from discord.ext import commands, tasks
from discord.ext.commands import Cog

from re import search
from datetime import datetime, timedelta
from better_profanity import profanity
from sqlalchemy import text
import settings
import asyncio
import traceback
import sys


whitelist = []
with open('resources/whitelist.txt', 'r') as f:
    whitelist = [line.strip() for line in f]

profanity.load_censor_words_from_file('resources/blacklist.txt', whitelist_words=whitelist)


class ModCommands(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None
        self.check_member_status.start()
        self.url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        self.invite_regex = r"(?:https?://)?discord(?:(?:app)?\.com/invite|\.gg)/?[a-zA-Z0-9]+/?"
        self.logs_channel = self.client.get_channel(settings.config["channels"]["log"])

    async def remove_member_role(self, ctx, user, member_role, noperms=False):
        await user.remove_roles(member_role)
        await utils.doembed(ctx, "Member", f"{user} no longer has member!", f"Member taken by: <@{ctx.author.id}>.", user)
        if noperms:
            await database.mod_event_insert(user.id, 11, datetime.utcnow(), None, ctx.author.id, 0)
        else:
            await database.mod_event_insert(user.id, 9, datetime.utcnow(), None, ctx.author.id, 0)
            await database.userdata_update_query(user.id, {'member': 0})

    async def add_member_role(self, ctx, user, member_role):
        await user.add_roles(member_role)
        await utils.doembed(ctx, "Member", f"{user} has been given member!", f"Member given by: <@{ctx.author.id}>.", user)
        await database.mod_event_insert(user.id, 8, datetime.utcnow(), None, ctx.author.id, 0)
        await database.userdata_update_query(user.id, {'member': 1})

    async def dm_user(self, ctx, user, content):
        try:
            await user.send(content)
        except discord.errors.Forbidden:
            await ctx.send('Message could not be delivered because this user has their dms closed')
            return False
        else:
            return True


    @commands.command(name='d')
    @commands.check(utils.NotInBump)
    async def dBumpChannel(self, ctx, *, args):
        await ctx.message.delete()
        await ctx.send(f'Wrong channel! Please bump the server in <#{settings.config["channels"]["bump"]}>', delete_after=5)
    @dBumpChannel.error
    async def dBumpChannel_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            pass
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


    @commands.command(name='selfmute')
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
    async def selfmute(self, ctx):
        """Lets the user selfmute taking them out of the server"""
        Selfmute_Role = ctx.guild.get_role(settings.config["statusRoles"]["self-mute"])
        if Selfmute_Role in ctx.author.roles:
            await ctx.author.remove_roles(Selfmute_Role)
        else:
            await ctx.author.add_roles(Selfmute_Role)


    @commands.command(name="purge", aliases=["clear"])
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"])
    async def purge(self, ctx, amount=5):
        """clears messages in the given channel"""
        if amount > 50:
            await ctx.send('You cannot purge more than 50 messages at a time')
        else:
            await ctx.message.delete()
            await ctx.channel.purge(limit=amount)


    @commands.command(name='noperms')
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"])
    async def memeber(self, ctx, user: discord.Member):
        await self.client.wait_until_ready()
        result = await database.userdata_select_query(user.id, False)
        if result and result[12] != 0:
            mod = await utils.in_roles(ctx.author, settings.config["staffRoles"]["moderator"])
            if mod:
                await database.userdata_update_query(user.id, {'noperms': 0})
                await database.mod_event_insert(user.id, 12, datetime.utcnow(), None, ctx.author.id, 0)
                await utils.emoji(ctx)
            else:
                await ctx.send("Only moderators and above can remove NoPerms")
        else:
            await self.remove_member_role(ctx, user, ctx.guild.get_role(settings.config["statusRoles"]["member"]))
            await database.userdata_update_query(user.id, {'noperms': 1})
            await database.mod_event_insert(user.id, 11, datetime.utcnow(), None, ctx.author.id, 0)
            await utils.emoji(ctx)


    @commands.command(name="member")
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"])
    async def member(self, ctx, user: discord.Member):
        await self.client.wait_until_ready()
        member_joined_at = user.joined_at
        result = await database.userdata_select_query(user.id, False)
        if result and result[12] != 0:
            member_joined_at = (datetime.fromtimestamp((result[12])) -
                                timedelta(hours=settings.config["memberUpdateInterval"]))
        member_role = ctx.guild.get_role(settings.config["statusRoles"]["member"])
        if member_role in user.roles:
            await self.remove_member_role(ctx, user, member_role)
            await utils.emoji(ctx)

        else:
            if datetime.utcnow() >= (member_joined_at + timedelta(hours=settings.config["memberCommandThreshold"])):
                if result and result[11] != 1:
                    await self.add_member_role(ctx, user, member_role)
                    await utils.emoji(ctx)
                else:
                    await ctx.send('User current has NoPerms role')
            elif result[11] == 1:
                await ctx.send("User current has NoPerms role")
            else:
                await ctx.send("User has not been around long enough to be automatically given member.")


    @commands.command(name="mute", aliases=['s', 'strike'])
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"])
    async def mute(self, ctx, user: discord.Member, *, reason=None):
        """Generic mute command, gives the user the muted role and adds details to the mod event table

        Args:
            user : This is the user you want to mute
            reason: This the the reason for the mute, please keep it consise and relevant for future refrence
        """
        await self.client.wait_until_ready()
        muted = await utils.in_roles(user, settings.config["statusRoles"]["muted"])
        member_role = ctx.guild.get_role(settings.config["statusRoles"]["member"])
        if member_role in user.roles:
            if not await utils.is_staff(user):
                await self.remove_member_role(ctx, user, member_role)
        if muted:
            await self.client.wait_until_ready()
            double_role = ctx.guild.get_role(settings.config["statusRoles"]["double-muted"])
            await user.add_roles(double_role)
            await utils.doembed(ctx, "DoubleMute", f"{user} has been Double Muted!", f"Muted by: <@{ctx.author.id}>.", user)
            await database.mod_event_insert(user.id, 10, datetime.utcnow(), reason, ctx.author.id, 0)
            await database.userdata_update_query(user.id, {'double_mute': 1})
            await utils.emoji(ctx)
        else:
            if reason is None:
                await ctx.channel.send('please give reason for mute', delete_after=5)
            else:
                await user.add_roles(ctx.guild.get_role(settings.config["statusRoles"]["muted"]))
                await utils.doembed(ctx, "Mute", f"{user} has been Muted!", f"**for:** {reason} Muted by: <@{ctx.author.id}>.", user)
                await database.mod_event_insert(user.id, 3, datetime.utcnow(), reason, ctx.author.id, 0)
                await database.userdata_update_query(user.id, {'mute': 1})
                await utils.emoji(ctx)


    @commands.command(name="vmute", aliases=['vs', 'vstrike'])
    @commands.cooldown(1, 86400, commands.BucketType.user)
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
        settings.config["statusRoles"]["vip"],
        settings.config["statusRoles"]["boost-vip"])
    async def vmute(self, ctx, user: discord.Member, *, reason=None):
        """A version of the mute command but for VIPs, has the same functionality of giving the user the mute role, and adding the event to the mod event table, but has a cooldown.
        Please be aware, abuse of this command will result in the VIP role being removed

        Args:
            user : This is the user you want to mute
            reason: This the the reason for the mute, please keep it consise and relevant for future refrence
        """
        await self.client.wait_until_ready()
        muted = False
        Mute_role = ctx.guild.get_role(settings.config["statusRoles"]["muted"])
        member_role = ctx.guild.get_role(settings.config["statusRoles"]["member"])
        for role in user.roles:
            if role.id == Mute_role.id:
                muted = True
        if member_role in user.roles:
            if not await utils.is_staff(user):
                await self.remove_member_role(self, ctx, user, member_role)
        if muted:
            pass
        if user is ctx.author:
            await ctx.send('you cannot mute yourself')
        else:
            if reason is None:
                await ctx.channel.send('please give reason for mute', delete_after=5)
            else:
                await user.add_roles(ctx.guild.get_role(settings.config["statusRoles"]["muted"]))
                await utils.doembed(ctx, "Mute", f"{user} has been Muted!", f"**for:** {reason} Muted by: <@{ctx.author.id}>.", user)
                await database.mod_event_insert(user.id, 3, datetime.utcnow(), reason, ctx.author.id, 0)
                await database.userdata_update_query(user.id, {'mute': 1})
                await utils.emoji(ctx)


    @commands.command(name="cooldown", aliases=['c'])
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"])
    async def cooldown(self, ctx, user: discord.Member, *, time: utils.TimeConverter = None):
        """takes the user out of the general channel for a specific amount of time"""
        cooldown_role = user.guild.get_role(settings.config["statusRoles"]["cooldown"])
        if time:
            better_time = await utils.convert_from_seconds(time)
            await user.add_roles(cooldown_role)
            await utils.doembed(ctx, "Cooldown", f'{user} cooled-down by {ctx.author}', f'The cooldown will be removed in {better_time}', user)
            await database.mod_event_insert(user.id, 5, datetime.utcnow(), None, ctx.author.id, 0)
            await database.userdata_update_query(user.id, {'cooldown': 1})
            await asyncio.sleep(time)
            await user.remove_roles(cooldown_role)
            await utils.doembed(ctx, "Cooldown", f'{user} is no longer cooled-down', 'The cooldown was removed automatically by the bot', user)
            make_historical_query = text(f'update mod_event set historical = 1 '
                                         f'where recipient_id = {user.id} and event_type = 5')
            database.conn.execute(make_historical_query)
            await database.userdata_update_query(user.id, {'cooldown': 0})
        else:
            await ctx.send('Please give a timer for the cooldown')


    @commands.command(name="unmute")
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"])
    async def unmute(self, ctx, user: discord.Member = None, *, time: utils.TimeConverter = None):
        """unmutes the user in question

        Args:
            user: This is the user you wish to unmute.
            time: This is the timer, however this defaults to 0. Please enter your timer in the format 1h 3m 2s
        """
        await self.client.wait_until_ready()
        if user is None:
            await ctx.send('Please tag the user you want to unmute', delete_after=5)

        else:
            muted = False
            self_muted = False
            double = False
            self_mute_role = ctx.guild.get_role(settings.config["statusRoles"]["self-mute"])
            muted_role = ctx.guild.get_role(settings.config["statusRoles"]["muted"])
            double_role = ctx.guild.get_role(settings.config["statusRoles"]["double-muted"])
            if time:
                better_time = await utils.convert_from_seconds(time)
                await utils.doembed(ctx, "Unmute", f"{user} will be unmuted in {better_time}", f"Unmuted by: <@{ctx.author.id}>.", user)
                await asyncio.sleep(time)
            if muted_role in user.roles:
                if double_role not in user.roles:
                    await user.remove_roles(muted_role)
                    await utils.emoji(ctx)
                    muted = True
            if self_mute_role in user.roles:
                await user.remove_roles(self_mute_role)
                await utils.emoji(ctx)
                self_muted = True
            if double_role in user.roles:
                await user.remove_roles(double_role)
                await utils.emoji(ctx)
                double = True
            if muted or self_muted or double:
                await utils.doembed(ctx, "Unmute", f"{user} has been Unmuted!", f"Unmuted by: <@{ctx.author.id}>.", user)
                if not self_muted:
                    if muted and not double:
                        await database.mod_event_insert(user.id, 4, datetime.utcnow(), None, ctx.author.id, 0)
                        prior_mute_queries = text(f'update mod_event set historical = 1 where recipient_id = {user.id} '
                                                f'and event_type = 3 and historical = 0')
                        database.conn.execute(prior_mute_queries)
                        await database.userdata_update_query(user.id, {'mute': 0})
                    else:
                        await database.mod_event_insert(user.id, 4, datetime.utcnow(), None, ctx.author.id, 0)
                        prior_mute_queries = text(f'update mod_event set historical = 1 where recipient_id = {user.id} '
                                                f'and event_type = 10 and historical = 0')
                        database.conn.execute(prior_mute_queries)
                        await database.userdata_update_query(user.id, {'double_mute': 0})


    @commands.command(name="kick")
    @commands.cooldown(15, 600, commands.BucketType.user)
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"])
    async def kick(self, ctx, member: discord.User = None, *, reason=None):
        """kicks the user from the server"""
        if member is None or member == ctx.message.author:
            await ctx.channel.send("You cannot kick yourself")
            return
        if await utils.is_staff(member):
            await ctx.send('you cannot kick a memeber of staff')
            return
        if reason is None:
            reason = "For being a jerk!"
        await self.dm_user(ctx, member, f'You have been kicked from {ctx.guild.name}.\n\nReason: {reason}\nKicked by:{ctx.author.name}')
        await ctx.guild.kick(member, reason=reason)
        await utils.doembed(ctx, "Kick", f"{member} has been Kicked!", f"**for:** {reason} Kicked by: <@{ctx.author.id}>.", member)
        await database.mod_event_insert(member.id, 2, datetime.utcnow(), reason, ctx.author.id, 0)
        await database.userdata_update_query(member.id, {'kicked': 1})
        await utils.emoji(ctx)


    @commands.command(name='underage')
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"])
    async def underage(self, ctx, member: discord.Member):
        underage_role = ctx.guild.get_role(settings.config["statusRoles"]["underage"])
        await member.add_roles(underage_role)
        await utils.emoji(ctx)


    @commands.command(name="ban")
    @commands.cooldown(15, 600, commands.BucketType.user)
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"])
    async def ban(self, ctx, member: discord.User = None, *, reason=None, purge=False):
        """Generic command to ban a user to the server.  this command can only be exectued three times in a row by the same moderator

        Args
            member: This is the user you intend to ban.
            reason: This is the reason for the ban.
            purge: This is weather or not you want to purge the users past 24 hours of messages, this defaults to false. If you want to purge type in True.
        """
        if member is None or member == ctx.message.author:
            await ctx.channel.send("You cannot Ban yourself")
            return
        if await utils.is_staff(member):
            await ctx.send('you cannot kick a memeber of staff')
            return
        if reason is None:
            reason = "For being a jerk!"
        await self.dm_user(ctx, member, f'You have been banned from {ctx.guild.name}.\n\nReason: {reason}\nKicked by:{ctx.author.name}')
        if purge:
            await ctx.guild.ban(member, reason=reason, delete_message_days=1)
        else:
            await ctx.guild.ban(member, reason=reason)
        await utils.doembed(ctx, "Ban", f"{member} has been Banned!", f"**for:** {reason} banned by: <@{ctx.author.id}>.", member)
        await database.mod_event_insert(member.id, 1, datetime.utcnow(), reason, ctx.author.id, 0)
        await database.update(member.id, {'banned': 1})
        await utils.emoji(ctx)


    @commands.command(name="automod")
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"])
    async def automod_edit(self, ctx, arg=None, *words):
        invarg = 'Please use the corect arguments\n```!automod add - add word to blacklist\n!automod remove - remove word from blacklist\n!automod blacklist - to see the blacklist```'
        devlogs = self.client.get_channel(settings.config["channels"]["devlog"])
        if arg is None:
            await ctx.send(invarg)
        elif arg == 'add':
            with open('resources/blacklist.txt', "a", encoding="utf-8") as f:
                f.write("".join([f"{w}\n" for w in words]))
                await utils.emoji(ctx)
            profanity.load_censor_words_from_file('resources/blacklist.txt', whitelist_words=whitelist)
            await devlogs.send(f'{utils.timestr}Reloaded `blacklist.txt` and `whitelist.txt` due to edit')
        elif arg == 'remove':
            with open('resources/blacklist.txt', "r", encoding="utf-8") as f:
                stored = [w.strip() for w in f.readlines()]
            with open('resources/blacklist.txt', "w", encoding="utf-8") as f:
                f.write("".join([f"{w}\n" for w in stored if w not in words]))
                profanity.load_censor_words_from_file('resources/blacklist.txt', whitelist_words=whitelist)
                await devlogs.send(f'{utils.timestr}Reloaded `blacklist.txt` and `whitelist.txt` due to edit')
            await utils.emoji(ctx)
        elif arg == 'blacklist':
            await ctx.send(file=File('resources/blacklist.txt'))
        else:
            await ctx.send(invarg)


    @commands.command(name='rule', aliases=['rules'])
    @commands.cooldown(1, 5)
    async def rules(self, ctx, rule: int = None):
        if rule is not None:
            rules = await utils.extract_data('resources/rules.txt')
            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
            embed.set_author(name="Rules", icon_url=ctx.author.avatar_url)
            embed.add_field(name=f"Rule {rule}", value=rules[rule - 1])
            await ctx.send(embed=embed)
            # Couldnt get this working w/ utils.doembed for some reason, this is something thall have to be addressed in the future


    @commands.command(name="lynch")
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
        settings.config["statusRoles"]["member"])
    async def nlynch(self, ctx, member: discord.Member = None):
        """A command to be used if there is no staff present, where three members can type in `!lynch` in order to mute a user"""
        if member is None:
            await ctx.send('please tag the user you want to lynch', delete_after=5)
        elif ctx.author == member:
            await ctx.channel.send("You can't lynch yourself!")
            return
        if await utils.is_staff(member):
            await ctx.send('you cannot kick a memeber of staff')
            return
        result = database.userdata_select_query(member.id, False)
        if result:
            current_lynches = result[5] + 1
            if datetime.utcnow() > (datetime.fromtimestamp(result[7]) + timedelta(hours=8)):
                current_lynches = 1
                make_historical_query = text(f'update mod_event set historical = 1 '
                                             f'where recipient_id = {member.id} and event_type = 6')
                database.conn.execute(make_historical_query)
            successful_lynches = result[6]
            if current_lynches >= 3:
                await ctx.channel.send(f'{member.mention} has been lynched')
                await database.userdata_update_query(member.id, {'lynch_count': 0, 'successful_lynch_count': successful_lynches + 1, 'lynch_expiration_time': 0})
                lynch_role = ctx.guild.get_role(settings.config["statusRoles"]["muted"])
                await member.add_roles(lynch_role)
                await database.mod_event_insert(member.id, 6, datetime.utcnow(), None, ctx.author.id, 0)
                find_lynches_query = text(f'select issuer_id from mod_event where recipient_id = {member.id} '
                                          f'and event_type = 6 and historical = 0')
                lynchers = database.conn.execute(find_lynches_query)
                lyncher_list = ""
                for lyncher in lynchers:
                    lyncher_list += self.client.get_user(lyncher[0]).mention + " "
                bot = ctx.guild.get_member(settings.config["botId"])
                await utils.doembed(ctx, "Lynch", f"User {member} was lynched! ", f"lynched by: {lyncher_list}", bot)
            else:
                await utils.emoji(ctx)
                await database.update(member.id, {'lynch_count': current_lynches, 'lynch_expiration_time': (datetime.utcnow() + timedelta(hours=8)).timestamp()})
                await database.mod_event_insert(member.id, 6, datetime.utcnow(), None, ctx.author.id, 0)
            member_role = ctx.guild.get_role(settings.config["statusRoles"]["member"])
            await ctx.author.remove_roles(member_role)


    @commands.command(name="dm", aliases=['message'])
    @commands.check(utils.is_in_complaint_channel)
    async def dm(self, ctx, member: discord.Member, *, content):
        """messages the given user through the bot"""
        succsess = await self.dm_user(ctx, member, content)
        if succsess:
            await utils.emoji(ctx)
    @dm.error
    async def dm_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await utils.emoji(ctx, '❌')
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('You cant send an empty message')
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


    @Cog.listener()
    async def on_message(self, message):
        if settings.config["prefix"] == "!":
            if message.guild is None:
                await self.modMail(message)
            elif not await utils.is_staff(message.author) \
                    and not await utils.in_roles(message.author, settings.config["statusRoles"]["bot-role"]):
                await self.websiteBlacklist(message)
                member = await utils.in_roles(message.author, settings.config["statusRoles"]["member"])
                await self.spamFilter(message)
                if profanity.contains_profanity(message.content):
                    await message.delete()
                elif not member and search(self.url_regex, message.content):
                    await message.delete()
                elif search(self.invite_regex, message.content):
                    await message.delete()
                    await self.logs_channel.send(f'<@{message.author.id}> tried to post:\n{message.content}')

    async def modMail(self, message):
        complaints_channel = self.client.get_channel(settings.config["channels"]["complaints"])
        if message.author.id != settings.config["botId"]:
            await complaints_channel.send(f"<@{message.author.id}> said: {message.content}")

    async def websiteBlacklist(self, message):
        with open(settings.config["websiteBlacklistFilePath"]) as blocked_file:
            for website in blocked_file:
                website = website.replace("\n", "")
                if website in message.content:
                    dev_chat = self.client.get_channel(settings.config["channels"]["development"])
                    if message.author.id == settings.config["botId"]:
                        if message.channel.id != settings.config["channels"]["development"]:
                            await dev_chat.send(f'{message.author.name} tried to post ```{message.content}```')
                            break
                    else:
                        await message.delete()
                        staff_chat = self.client.get_channel(settings.config["channels"]["staff-lounge"])
                        await staff_chat.send(f'{message.author.name} tried to post a link from the blacklist.')
                        break

    async def spamFilter(self, message):
        def _check(m):
            return (m.author == message.author and len(m.mentions) and (datetime.utcnow()-m.created_at).seconds < 15)
        if len((list(filter(lambda m: _check(m), self.client.cached_messages)))) >= 5:
            await message.author.add_roles(message.guild.get_role(settings.config["statusRoles"]["muted"]))
            embed = discord.Embed(color=message.author.color, timestamp=message.created_at)
            embed.set_author(name="Mute", icon_url=message.author.avatar_url)
            embed.add_field(name=f"{message.author} has been Muted! ", value="muted for mention spamming")
            await self.logs_channel.send(embed=embed)
            reason = 'auto muted for spam pinging'
            await database.mod_event_insert(message.author.id, 3, datetime.utcnow(), reason, settings.config["botId"], 0)
            await database.update(message.author.id, {'mute': 1})

    @tasks.loop(hours=settings.config["memberUpdateInterval"])
    async def check_member_status(self):
        prefix = settings.config["prefix"]
        if prefix == "!":
            make_historical_query = text('select id, member_activation_date from userdata')
            results = database.conn.execute(make_historical_query)
            current_guild = self.client.get_guild(settings.config["serverId"])
            for result in results:
                user = current_guild.get_member(result[0])
                if user is not None and \
                    result[1] != 0 and \
                        (datetime.fromtimestamp(result[1])) < datetime.utcnow() < (
                        datetime.fromtimestamp(result[1]) +
                        timedelta(hours=settings.config["memberUpdateInterval"])):
                    member_role = current_guild.get_role(settings.config["statusRoles"]["member"])
                    await user.add_roles(member_role)
                    await database.mod_event_insert(user.id, 8, datetime.utcnow(), None, settings.config["botId"], 0)
                    await database.userdata_update_query(user.id, {'member': 1})
                    # user_data_query = update(utils.userdata).where(utils.userdata.c.id == result[0]) \
                    #     .values(member_activation_date=0)
                    # utils.conn.execute(user_data_query)
                    # Discuss idea of zeroing out instead so that anomalies don't occur but data will be lost.

    @Cog.listener()
    async def on_member_update(self, before_user, after_user):
        if after_user.nick != before_user.nick:
            before = before_user.nick
            after = after_user.nick
            if before_user.nick is None:
                before = before_user.display_name + '#' + before_user.discriminator
            if after_user.nick is None:
                after = after_user.display_name + '#' + after_user.discriminator
            await database.name_change_event_insert(after_user.id, before, 2, after)


    @Cog.listener()
    async def on_user_update(self, before_user, after_user):
        if before_user.display_name != after_user.display_name or before_user.discriminator != after_user.discriminator:
            before = before_user.display_name + '#' + before_user.discriminator
            after = after_user.display_name + '#' + after_user.discriminator
            await database.name_change_event_insert(after_user.id, before, 1, after)


def setup(client):
    client.add_cog(ModCommands(client))
