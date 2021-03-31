import discord
from discord.ext import commands

from datetime import datetime, timedelta
import asyncio

import utils
import settings
import database
from sqlalchemy import text
import sys
import traceback


class ModCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.guild = self.client.get_guild(settings.config["serverId"])

        self.member_role = self.guild.get_role(settings.config["statusRoles"]["member"])
        self.mute_role = self.guild.get_role(settings.config["statusRoles"]["muted"])
        self.double_mute_role = self.guild.get_role(
            settings.config["statusRoles"]["double-muted"]
        )
        self.cooldown_role = self.guild.get_role(
            settings.config["statusRoles"]["cooldown"]
        )
        self.underage_role = self.guild.get_role(
            settings.config["statusRoles"]["underage"]
        )

    async def remove_member_role(self, ctx, user, noperms=False):
        await user.remove_roles(self.member_role)
        await utils.doembed(
            ctx,
            "Member",
            f"{user} no longer has member!",
            f"Member taken by: <@{ctx.author.id}>.",
            user,
        )
        if noperms:
            await database.mod_event_insert(
                user.id, 11, datetime.utcnow(), None, ctx.author.id, 0
            )
        else:
            await database.mod_event_insert(
                user.id, 9, datetime.utcnow(), None, ctx.author.id, 0
            )
            await database.userdata_update_query(user.id, {"member": 0})

    async def add_member_role(self, ctx, user):
        await user.add_roles(self.member_role)
        await utils.doembed(
            ctx,
            "Member",
            f"{user} has been given member!",
            f"Member given by: <@{ctx.author.id}>.",
            user,
        )
        await database.mod_event_insert(
            user.id, 8, datetime.utcnow(), None, ctx.author.id, 0
        )
        await database.userdata_update_query(user.id, {"member": 1})

    async def dm_user(self, ctx, user, content):
        try:
            await user.send(content)
        except discord.errors.Forbidden:
            await ctx.send(
                "Message could not be delivered because this user has their dms closed"
            )
            return False
        else:
            return True

    @commands.command(name="d")
    @commands.check(utils.NotInBump)
    async def dBumpChannel(self, ctx, *, args):
        await ctx.message.delete()
        await ctx.send(
            f'Wrong channel! Please bump the server in <#{settings.config["channels"]["bump"]}>',
            delete_after=5,
        )

    @dBumpChannel.error
    async def dBumpChannel_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            pass
        else:
            print("\n--------", file=sys.stderr)
            print(f"Time      : {utils.timestr}", file=sys.stderr)
            print(f"Command   : {ctx.command}", file=sys.stderr)
            print(f"Message   : {ctx.message.content}", file=sys.stderr)
            print(f"Author    : {ctx.author}", file=sys.stderr)
            print(" ", file=sys.stderr)
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )

    @commands.command(name="kick")
    @commands.cooldown(15, 600, commands.BucketType.user)
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
    )
    async def kick(self, ctx, member: discord.Member = None, *, reason=None):
        """kicks the user from the server"""
        if member is None or member == ctx.message.author:
            return
        if await utils.is_staff(member):
            return
        if reason is None:
            reason = "For being a jerk!"

        await self.dm_user(
            ctx,
            member,
            f"You have been kicked from {ctx.guild.name}.\n\nReason: {reason}\nKicked by:{ctx.author.name}",
        )
        await ctx.guild.kick(member, reason=reason)
        await utils.doembed(
            ctx,
            "Kick",
            f"{member} has been Kicked!",
            f"**for:** {reason} Kicked by: <@{ctx.author.id}>.",
            member,
        )
        await database.mod_event_insert(
            member.id, 2, datetime.utcnow(), reason, ctx.author.id, 0
        )
        await database.userdata_update_query(member.id, {"kicked": 1})
        await utils.emoji(ctx)

    @commands.command(name="ban")
    @commands.cooldown(15, 600, commands.BucketType.user)
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
    )
    async def ban(
        self, ctx, member: discord.Member = None, *, reason=None, purge=False
    ):
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
            await ctx.send("you cannot ban a memeber of staff")
            return
        if reason is None:
            reason = "For being a jerk!"
        await self.dm_user(
            ctx,
            member,
            f"You have been banned from {ctx.guild.name}.\n\nReason: {reason}\nKicked by:{ctx.author.name}",
        )
        if purge:
            await ctx.guild.ban(member, reason=reason, delete_message_days=1)
        else:
            await ctx.guild.ban(member, reason=reason)
        await utils.doembed(
            ctx,
            "Ban",
            f"{member} has been Banned!",
            f"**for:** {reason} banned by: <@{ctx.author.id}>.",
            member,
        )
        await database.mod_event_insert(
            member.id, 1, datetime.utcnow(), reason, ctx.author.id, 0
        )
        await database.userdata_update_query(member.id, {"banned": 1})
        await utils.emoji(ctx)

    @commands.command(name="member")
    @commands.cooldown(1, 10)
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
    )
    async def member(self, ctx, user: discord.Member = None):
        if user is None:
            return
        member_joined_at = user.joined_at
        result = await database.userdata_select_query(user.id, False)
        if result and result[12] != 0:
            member_joined_at = datetime.fromtimestamp((result[12])) - timedelta(
                hours=settings.config["memberUpdateInterval"]
            )
        if await utils.in_roles(user, self.member_role.id):
            await self.remove_member_role(ctx, user)
            await utils.emoji(ctx)
        else:
            if result[11] == 1:
                await ctx.send("User has NoPerms role")
                return
            if datetime.utcnow() >= (
                member_joined_at
                + timedelta(hours=settings.config["memberCommandThreshold"])
            ):
                await self.add_member_role(ctx, user)
                await utils.emoji(ctx)
            else:
                await ctx.send(
                    "User has not been around long enough to be automatically given member."
                )

    @commands.command(name="noperms")
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
    )
    async def memeber(self, ctx, user: discord.Member):
        """Adds a noperms flag to the user inside the bots database. This does not add the role
        If a user has a noperms flag this means that a memeber of staff cannot give the the memeber role without removing the flag.
        While Semi's can add the flag, same as full moderators; only full moderators can remove the flag"""
        if user is None:
            return
        result = await database.userdata_select_query(user.id, False)
        if result and result[12] != 0:
            if await utils.in_roles(
                ctx.author, settings.config["staffRoles"]["moderator"]
            ):
                await database.userdata_update_query(user.id, {"noperms": 0})
                await database.mod_event_insert(
                    user.id, 12, datetime.utcnow(), None, ctx.author.id, 0
                )
                await utils.emoji(ctx)
        else:
            await self.remove_member_role(ctx, user, True)
            await database.userdata_update_query(user.id, {"noperms": 1})
            await database.mod_event_insert(
                user.id, 11, datetime.utcnow(), None, ctx.author.id, 0
            )
            await utils.emoji(ctx)

    @commands.command(name="underage")
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
    )
    async def underage(self, ctx, member: discord.Member):
        await member.add_roles(self.underage_role)
        await utils.emoji(ctx)

    @commands.command(name="mute", aliases=["s", "strike"])
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
    )
    async def gmute(self, ctx, user: discord.Member, *, reason=None):
        """Generic mute command, gives the user the muted role and adds details to the mod event table

        Args:
            user : This is the user you want to mute
            reason: This the the reason for the mute, please keep it consise and relevant for future refrence
        """
        await self.mute(ctx, user, reason)

    @commands.command(name="vmute", aliases=["vs", "vstrike"])
    @commands.cooldown(1, 86400, commands.BucketType.user)
    @commands.has_any_role(
        settings.config["statusRoles"]["vip"],
    )
    async def vmute(self, ctx, user: discord.Member, *, reason=None):
        """A version of the mute command but for VIPs, has the same functionality of giving the user the mute role, and adding the event to the mod event table, but has a cooldown.
        Please be aware, abuse of this command will result in the VIP role being removed

        Args:
            user : This is the user you want to mute
            reason: This the the reason for the mute, please keep it consise and relevant for future refrence
        """
        await self.mute(ctx, user, reason, True)

    async def mute(self, ctx, user: discord.Member, reason, vip=False):
        if user is None:
            return
        if await utils.is_staff(user):
            return
        if await utils.in_roles(user, self.member_role.id):
            await self.remove_member_role(ctx, user)
        if await utils.in_roles(user, settings.config["statusRoles"]["muted"]):
            if not vip:
                await user.add_roles(self.double_mute_role)
                await utils.doembed(
                    ctx,
                    "DoubleMute",
                    f"{user} has been Double Muted!",
                    f"Muted by: <@{ctx.author.id}>.",
                    user,
                )
                await database.mod_event_insert(
                    user.id, 10, datetime.utcnow(), reason, ctx.author.id, 0
                )
                await database.userdata_update_query(user.id, {"double_mute": 1})
                await utils.emoji(ctx)
        else:
            if reason is None:
                await ctx.channel.send("please give reason for mute", delete_after=5)
                return
            await user.add_roles(self.mute_role)
            await utils.doembed(
                ctx,
                "Mute",
                f"{user} has been Muted!",
                f"**for:** {reason} Muted by: <@{ctx.author.id}>.",
                user,
            )
            await database.mod_event_insert(
                user.id, 3, datetime.utcnow(), reason, ctx.author.id, 0
            )
            await database.userdata_update_query(user.id, {"mute": 1})
            await utils.emoji(ctx)

    @commands.command(name="unmute")
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
    )
    async def unmute(
        self, ctx, user: discord.Member = None, *, time: utils.TimeConverter = None
    ):
        """unmutes the user in question

        Args:
            user: This is the user you wish to unmute.
            time: This is the timer, however this defaults to 0. Please enter your timer in the format 1h 3m 2s
        """
        if user is None:
            return
        if not await utils.in_roles(
            user, self.mute_role.id
        ) or not await utils.in_roles(user, self.double_mute_role.id):
            return
        if time:
            better_time = await utils.convert_from_seconds(time)
            await utils.doembed(
                ctx,
                "Unmute",
                f"{user} will be unmuted in {better_time}",
                f"Unmuted by: <@{ctx.author.id}>.",
                user,
            )
            await asyncio.sleep(time)

        if await utils.in_roles(user, self.double_mute_role.id):
            await self.undouble(ctx, user)
        else:
            await self.unmmute(ctx, user)
        if await utils.in_roles(user, self.mute_role.id) or await utils.in_roles(
            user, self.double_mute_role.id
        ):
            await utils.emoji(ctx)
            if time:
                better_time = await utils.convert_from_seconds(time)
                await utils.doembed(
                    ctx,
                    "Unmute",
                    f"{user} will be unmuted in {better_time}",
                    f"Unmuted by: <@{ctx.author.id}>.",
                    user,
                )
                await asyncio.sleep(time)
            if await utils.in_roles(user, self.double_mute_role.id):
                await self.undouble(ctx, user)
            else:
                await self.unmmute(ctx, user)

    async def unmmute(self, ctx, user):
        await user.remove_roles(self.mute_role)
        await utils.doembed(
            ctx,
            "Unmute",
            f"{user} has been Unmuted!",
            f"Unmuted by: <@{ctx.author.id}>.",
            user,
        )
        await database.mod_event_insert(
            user.id, 4, datetime.utcnow(), None, ctx.author.id, 0
        )
        prior_mute_queries = text(
            f"update mod_event set historical = 1 where recipient_id = {user.id} "
            f"and event_type = 3 and historical = 0"
        )
        database.conn.execute(prior_mute_queries)
        await database.userdata_update_query(user.id, {"mute": 0})

    async def undouble(self, ctx, user):
        await user.remove_roles(self.double_mute_role)
        await utils.doembed(
            ctx,
            "Unmute",
            f"{user} has been Un-double-muted!",
            f"Unmuted by: <@{ctx.author.id}>.",
            user,
        )
        await database.mod_event_insert(
            user.id, 4, datetime.utcnow(), None, ctx.author.id, 0
        )
        prior_mute_queries = text(
            f"update mod_event set historical = 1 where recipient_id = {user.id} "
            f"and event_type = 10 and historical = 0"
        )
        database.conn.execute(prior_mute_queries)
        await database.userdata_update_query(user.id, {"double_mute": 0})

    @commands.command(name="cooldown", aliases=["c"])
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
    )
    async def cooldown(
        self, ctx, user: discord.Member, *, time: utils.TimeConverter = None
    ):
        """takes the user out of the general channel for a specific amount of time"""
        if not time:
            return
        better_time = await utils.convert_from_seconds(time)
        await user.add_roles(self.cooldown_role)
        await utils.doembed(
            ctx,
            "Cooldown",
            f"{user} cooled-down by {ctx.author}",
            f"The cooldown will be removed in {better_time}",
            user,
        )
        await database.mod_event_insert(
            user.id, 5, datetime.utcnow(), None, ctx.author.id, 0
        )
        await database.userdata_update_query(user.id, {"cooldown": 1})
        await asyncio.sleep(time)
        await user.remove_roles(self.cooldown_role)
        await utils.doembed(
            ctx,
            "Cooldown",
            f"{user} is no longer cooled-down",
            "The cooldown was removed automatically by the bot",
            user,
        )
        make_historical_query = text(
            f"update mod_event set historical = 1 "
            f"where recipient_id = {user.id} and event_type = 5"
        )
        database.conn.execute(make_historical_query)
        await database.userdata_update_query(user.id, {"cooldown": 0})

    @commands.command(name="purge", aliases=["clear"])
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
    )
    async def purge(self, ctx, amount=5):
        """clears messages in the given channel"""
        if amount > 50:
            return
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount)

    @commands.command(name="lynch")
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
        settings.config["statusRoles"]["member"],
    )
    async def nlynch(self, ctx, member: discord.Member = None):
        """A command to be used if there is no staff present, where three members can type in `!lynch` in order to mute a user"""
        if member is None:
            return
        if ctx.author == member:
            return
        if await utils.is_staff(member):
            return

        result = database.userdata_select_query(member.id, False)
        if not result:
            return

        current_lynches = result[2] + 1
        if datetime.utcnow() > (datetime.fromtimestamp(result[4]) + timedelta(hours=8)):
            current_lynches = 1
            make_historical_query = text(
                f"update mod_event set historical = 1 "
                f"where recipient_id = {member.id} and event_type = 6"
            )
            database.conn.execute(make_historical_query)
        successful_lynches = result[3]
        if current_lynches >= 3:
            await ctx.channel.send(f"{member.mention} has been lynched")
            await database.userdata_update_query(
                member.id,
                {
                    "lynch_count": 0,
                    "successful_lynch_count": successful_lynches + 1,
                    "lynch_expiration_time": 0,
                },
            )
            await member.add_roles(self.mute_role)
            await database.mod_event_insert(
                member.id, 6, datetime.utcnow(), None, ctx.author.id, 0
            )
            find_lynches_query = text(
                f"select issuer_id from mod_event where recipient_id = {member.id} "
                f"and event_type = 6 and historical = 0"
            )
            lynchers = database.conn.execute(find_lynches_query)
            lyncher_list = ""
            for lyncher in lynchers:
                lyncher_list += self.client.get_user(lyncher[0]).mention + " "
            bot = ctx.guild.get_member(settings.config["botId"])
            await utils.doembed(
                ctx,
                "Lynch",
                f"User {member} was lynched! ",
                f"lynched by: {lyncher_list}",
                bot,
            )
        else:
            await utils.emoji(ctx)
            query = (
                database.update(database.userdata)
                .where(database.userdata.c.id == member.id)
                .values(
                    lynch_count=current_lynches,
                    lynch_expiration_time=(
                        datetime.utcnow() + timedelta(hours=8)
                    ).timestamp(),
                )
            )
            database.conn.execute(query)
            await database.mod_event_insert(
                member.id, 6, datetime.utcnow(), None, ctx.author.id, 0
            )
        await ctx.author.remove_roles(self.member_role)

    @commands.command(name="dm", aliases=["message"])
    @commands.check(utils.is_in_complaint_channel)
    async def dm(self, ctx, member: discord.Member, *, content):
        """messages the given user through the bot"""
        succsess = await self.dm_user(ctx, member, content)
        if succsess:
            await utils.emoji(ctx)

    @dm.error
    async def dm_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await utils.emoji(ctx, "❌")
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("You cant send an empty message")
        else:
            print("\n--------", file=sys.stderr)
            print(f"Time      : {utils.timestr}", file=sys.stderr)
            print(f"Command   : {ctx.command}", file=sys.stderr)
            print(f"Message   : {ctx.message.content}", file=sys.stderr)
            print(f"Author    : {ctx.author}", file=sys.stderr)
            print(" ", file=sys.stderr)
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )


def setup(client):
    client.add_cog(ModCommands(client))
