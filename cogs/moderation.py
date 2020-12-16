import discord
from discord import File
from discord.ext import commands, tasks
from discord.ext.commands import Cog

from re import search
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

url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
invite_regex = r"(?:https?://)?discord(?:(?:app)?\.com/invite|\.gg)/?[a-zA-Z0-9]+/?"

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


async def remove_member_role(self, ctx, user, member_role):
    await user.remove_roles(member_role)
    embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
    embed.set_author(name="Member", icon_url=user.avatar_url)
    embed.add_field(name=f"{user} has had their member role removed! ", value=f"Member removed by: <@{ctx.author.id}>.")
    channel = self.client.get_channel(settings.config["channels"]["log"])
    await channel.send(embed=embed)
    mod_query = utils.mod_event.insert(). \
        values(recipient_id=user.id, event_type=9, event_time=utils.datetime.now(),
               issuer_id=ctx.author.id, historical=0)
    utils.conn.execute(mod_query)
    user_data_query = update(utils.userdata).where(utils.userdata.c.id == user.id) \
        .values(member=0)
    utils.conn.execute(user_data_query)


async def add_member_role(self, ctx, user, member_role):
    await user.add_roles(member_role)
    embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
    embed.set_author(name="Member", icon_url=user.avatar_url)
    embed.add_field(name=f"{user} has been given member! ", value=f"Member given by: <@{ctx.author.id}>.")
    channel = self.client.get_channel(settings.config["channels"]["log"])
    await channel.send(embed=embed)
    mod_query = utils.mod_event.insert(). \
        values(recipient_id=user.id, event_type=8, event_time=utils.datetime.now(),
               issuer_id=ctx.author.id, historical=0)
    utils.conn.execute(mod_query)
    user_data_query = update(utils.userdata).where(utils.userdata.c.id == user.id) \
        .values(member=1)
    utils.conn.execute(user_data_query)


class ModCommands(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None
        self.check_member_status.start()

    @commands.command(name='selfmute')
    @commands.has_any_role(
        settings.config["statusRoles"]["member"])
    async def selfmute(self, ctx):
        """Lets the user selfmute taking them out of the server"""
        Selfmute_Role = ctx.guild.get_role(settings.config["statusRoles"]["self-mute"])
        logs_channel = self.client.get_channel(settings.config["channels"]["log"])
        if Selfmute_Role in ctx.author.roles:
            await ctx.author.remove_roles(Selfmute_Role)
            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
            embed.set_author(name="Selfmute", icon_url=ctx.author.avatar_url)
            embed.add_field(name=f'{ctx.author} selfmuted!', value='They shall remain inside the selfmute channel untill they choose to leave')
            await logs_channel.send(embed=embed)
        else:
            await ctx.author.add_roles(Selfmute_Role)
            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
            embed.set_author(name="Selfmute", icon_url=ctx.author.avatar_url)
            embed.add_field(name=f'{ctx.author} is no longer selfmuted!', value='They may run free amoungst the hills like a wild rabbit')
            await logs_channel.send(embed=embed)

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

    @commands.command(name="member")
    @commands.has_any_role(
        settings.config["statusRoles"]["moderator"],
        settings.config["statusRoles"]["semi-moderator"])
    async def member(self, ctx, user: discord.Member):
        await self.client.wait_until_ready()
        member_role = ctx.guild.get_role(settings.config["statusRoles"]["member"])
        if member_role in user.roles:
            await remove_member_role(self, ctx, user, member_role)
        else:
            await add_member_role(self, ctx, user, member_role)

    @commands.command(name="mute", aliases=['s', 'strike'])
    @commands.has_any_role(
        settings.config["statusRoles"]["moderator"],
        settings.config["statusRoles"]["semi-moderator"])
    async def mute(self, ctx, user: discord.Member, *, reason=None):
        """mutes the user and puts a strike against their name"""
        await self.client.wait_until_ready()
        if reason == None:
            await ctx.channel.send('please give reason for mute', delete_after=5)
        elif reason != None:
            channel = self.client.get_channel(settings.config["channels"]["log"])
            userAvatarUrl = user.avatar_url
            for discord.guild in self.client.guilds:
                Mute_role = user.guild.get_role(settings.config["statusRoles"]["muted"])
            #await user.send(
            #    f"Muted for '{reason}' by <@{ctx.author.id}>\nTo resolve this mute please communicate with the memeber of staff who muted you")
            await user.add_roles(Mute_role)
            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
            embed.set_author(name="Mute", icon_url=userAvatarUrl)
            embed.add_field(name=f"{user} has been Muted! ", value=f"**for:** {reason} Muted by: <@{ctx.author.id}>.")
            await channel.send(embed=embed)
            mod_query = utils.mod_event.insert(). \
                values(recipient_id=user.id, event_type=3, event_time=utils.datetime.now(), reason=reason,
                       issuer_id=ctx.author.id, historical=0)
            utils.conn.execute(mod_query)
            user_data_query = update(utils.userdata).where(utils.userdata.c.id == user.id) \
                    .values(mute=1)
            utils.conn.execute(user_data_query)

    @commands.command(name="cooldown", aliases=['c'])
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
            time_of_cooldown = utils.datetime.now()
            mod_query = utils.mod_event.insert(). \
                values(recipient_id=user.id, event_type=5, event_time=time_of_cooldown,
                       issuer_id=ctx.author.id, historical=0)
            utils.conn.execute(mod_query)
            user_data_query = update(utils.userdata).where(utils.userdata.c.id == user.id) \
                    .values(cooldown=1)
            utils.conn.execute(user_data_query)
            await asyncio.sleep(time)
            await user.remove_roles(cooldown_role)
            embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
            embed.set_author(name="user", icon_url=userAvatarUrl)
            embed.add_field(name=f'{user} is no longer cooled-down',
                            value=f'The cooldown was removed automatically by the bot')
            await logs_channel.send(embed=embed)
            make_historical_query = text(f'update mod_event set historical = 1 '
                                         f'where recipient_id = {user.id} and event_type = 5')
            utils.conn.execute(make_historical_query)
            user_data_query = update(utils.userdata).where(utils.userdata.c.id == user.id) \
                    .values(cooldown=0)
            utils.conn.execute(user_data_query)
        else:
            await ctx.send(f'Please give a timer for the cooldown')

    @commands.command(name="unmute")
    @commands.has_any_role(
        settings.config["statusRoles"]["moderator"],
                           settings.config["statusRoles"]["semi-moderator"])
    async def nunmute(self, ctx, user: discord.Member = None, *, time: TimeConverter = None):
        """unmute the user"""
        await self.client.wait_until_ready()
        if user == None:
            await ctx.send('Please tag the user you want to unmute', delete_after=5)
        else:
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
                    user_data_query = update(utils.userdata).where(utils.userdata.c.id == user.id) \
                        .values(mute=0)
                    utils.conn.execute(user_data_query)

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
        mod_query = utils.mod_event.insert(). \
            values(recipient_id=member.id, event_type=2, event_time=utils.datetime.now(), reason=reason,
                   issuer_id=ctx.author.id, historical=0)
        utils.conn.execute(mod_query)
        user_data_query = update(utils.userdata).where(utils.userdata.c.id == member.id) \
            .values(kicked=1)
        utils.conn.execute(user_data_query)

    @commands.command(name='underage')
    @commands.has_any_role(
        settings.config["statusRoles"]["moderator"],
        settings.config["statusRoles"]["semi-moderator"])
    async def underage(self, ctx, member: discord.Member):
        underage_role = ctx.guild.get_role(settings.config["statusRoles"]["underage"])
        await member.add_roles(underage_role)

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
        mod_query = utils.mod_event.insert(). \
            values(recipient_id=member.id, event_type=1, event_time=utils.datetime.now(), reason=reason,
                   issuer_id=ctx.author.id, historical=0)
        utils.conn.execute(mod_query)
        user_data_query = update(utils.userdata).where(utils.userdata.c.id == member.id) \
            .values(banned=1)
        utils.conn.execute(user_data_query)

    @commands.command(name="automod")
    @commands.has_any_role(
        settings.config["statusRoles"]["moderator"])
    async def automod_edit(self, ctx, arg=None, *words):
        invarg = 'Please use the corect arguments\n```!automod add - add word to blacklist\n!automod remove - remove word from blacklist\n!automod blacklist - to see the blacklist```'
        devlogs = self.client.get_channel(settings.config["channels"]["devlog"])
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
        elif arg == 'blacklist':
            await ctx.send(file = File('blacklist.txt'))
        else:
            await ctx.send(invarg)

    @commands.command(name="lynch")
    @commands.has_any_role(
        settings.config["statusRoles"]["member"],
        settings.config["statusRoles"]["moderator"],
        settings.config["statusRoles"]["semi-moderator"])
    async def nlynch(self, ctx, member: discord.Member = None):
        """A command to be used if there is no staff present, where three members can type in `!lynch` in order to mute a user"""
        if member == None:
            await ctx.send('please tag the user you want to lynch', delete_after=5)
        elif ctx.author == member:
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
                                          f'and event_type = 6 and historical = 0')
                lynchers = utils.conn.execute(find_lynches_query)
                lyncher_list = ""
                for lyncher in lynchers:
                    lyncher_list += self.client.get_user(lyncher[0]).mention + " "
                channel = self.client.get_channel(settings.config["channels"]["log"])  # log
                userAvatarUrl = 'https://cdn.discordapp.com/avatars/749836263955103774/d95c04a16c2bad01a4451c97fae42766.webp?size=1024'
                bot_role = ctx.guild.get_role(settings.config["statusRoles"]["bot-role"])
                embed = discord.Embed(color=bot_role.color, timestamp=ctx.message.created_at)
                embed.set_author(name="Lynch", icon_url=userAvatarUrl)
                embed.add_field(name=f"User {member} was lynched! ", value=f"lynched by: {lyncher_list}")
                await channel.send(embed=embed)
            else:
                await ctx.channel.send(f'lynch acknowledged', delete_after=5)
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
    
    @commands.command(name="dm", aliases=['message'])
    @commands.check(utils.is_in_complaint_channel)
    async def dm(self, ctx, member: discord.Member, *, content):
        """messages the given user through the bot"""
        channel = await member.create_dm()
        await channel.send(content)
        emoji = '✅'
        await ctx.message.add_reaction(emoji)
    @dm.error
    async def dm_handler(self, ctx, error):
        emoji = '❌'
        if isinstance(error, commands.CheckFailure):
            await ctx.message.add_reaction(emoji)

    @Cog.listener()
    async def on_message(self, message):
        prefix = settings.config["prefix"]
        bot_id = settings.config["botId"]
        if prefix == "!":
            complaints_channel = self.client.get_channel(settings.config["channels"]["complaints"])
            if message.guild is None:
                if message.author.id != bot_id:
                    await complaints_channel.send(f"<@{message.author.id}> said: {message.content}")
            else:
                with open(settings.config["websiteBlacklistFilePath"]) as blocked_file:
                    for website in blocked_file:
                        website = website.replace("\n", "")
                        if website in message.content:
                            await message.delete()
                            staff_chat = self.client.get_channel(settings.config["channels"]["staff-lounge"])
                            await staff_chat.send(f'{message.author.name} tried to post a link from the blacklist.')
                            break
                member = False
                #I would like to add a staff check to allow staff memebers to post invite links however i dont know how to do this, this is a job for the future
                member_role = message.guild.get_role(settings.config["statusRoles"]["member"])
                muted_role = message.guild.get_role(settings.config["statusRoles"]["muted"])
                logs_channel = message.guild.get_channel(settings.config["channels"]["log"])
                author = message.author
                userAvatarUrl = author.avatar_url
                def _check(m):
                    return (m.author == author and len(m.mentions) and (datetime.utcnow()-m.created_at).seconds < 15)
                if type(author) is discord.User:
                    return
                for role in author.roles:
                    if role.id == member_role.id:
                        member = True
                if not author.bot:
                    if len((list(filter(lambda m: _check(m), self.client.cached_messages)))) >=5:
                        await author.add_roles(muted_role)
                        embed = discord.Embed(color=author.color, timestamp=message.created_at)
                        embed.set_author(name="Mute", icon_url=userAvatarUrl)
                        embed.add_field(name=f"{author} has been Muted! ", value=f"muted for mention spamming")
                        await logs_channel.send(embed=embed)
                        reason = 'auto muted for spam pinging'
                        mod_query = utils.mod_event.insert(). \
                            values(recipient_id=author.id, event_type=3, event_time=utils.datetime.now(), reason=reason,
                                issuer_id=bot_id, historical=0)
                        utils.conn.execute(mod_query)
                        user_data_query = update(utils.userdata).where(utils.userdata.c.id == author.id) \
                                .values(mute=1)
                        utils.conn.execute(user_data_query)
                    if profanity.contains_profanity(message.content):
                        await message.delete()
                    elif not member and search(url_regex, message.content):
                        await message.delete()
                    elif search(invite_regex, message.content):
                        await message.delete()
                        await logs_channel.send(f'<@{author.id}> tried to post:\n{message.content}') #This works but there is currently a conflict with manger in logs channel, this will be fixed when manager is removed

    @tasks.loop(hours=settings.config["memberUpdateInterval"])
    async def check_member_status(self):
        prefix = settings.config["prefix"]
        if prefix == "!":
            make_historical_query = text(f'select id, member_activation_date from userdata')
            results = utils.conn.execute(make_historical_query)
            current_guild = self.client.get_guild(settings.config["serverId"])
            for result in results:
                user = current_guild.get_member(result[0])
                if user is not None and \
                    result[1] != 0 and \
                        (utils.datetime.fromtimestamp(result[1])) < utils.datetime.now() < (
                        utils.datetime.fromtimestamp(result[1]) +
                        utils.timedelta(hours=settings.config["memberUpdateInterval"])):
                    member_role = current_guild.get_role(settings.config["statusRoles"]["member"])
                    await user.add_roles(member_role)
                    mod_query = utils.mod_event.insert(). \
                        values(recipient_id=user.id, event_type=8, event_time=utils.datetime.now(),
                            issuer_id=settings.config["botId"], historical=0)
                    utils.conn.execute(mod_query)
                    user_data_query = update(utils.userdata).where(utils.userdata.c.id == user.id) \
                        .values(member=1)
                    utils.conn.execute(user_data_query)
                    # user_data_query = update(utils.userdata).where(utils.userdata.c.id == result[0]) \
                    #     .values(member_activation_date=0)
                    # utils.conn.execute(user_data_query)
                    # Discuss idea of zeroing out instead so that anomalies don't occur but data will be lost.


def setup(client):
    client.add_cog(ModCommands(client))
