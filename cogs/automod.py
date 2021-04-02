import discord
from discord import File
from discord.ext import commands, tasks
from discord.ext.commands import Cog

from re import search
from datetime import datetime, timedelta
from better_profanity import profanity
from sqlalchemy import text
import settings

import utils
import database


whitelist = []
with open("resources/whitelist.txt", "r") as f:
    whitelist = [line.strip() for line in f]

profanity.load_censor_words_from_file(
    "resources/blacklist.txt", whitelist_words=whitelist
)


class ModCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._last_member = None
        self.check_member_status.start()
        self.url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        self.invite_regex = (
            r"(?:https?://)?discord(?:(?:app)?\.com/invite|\.gg)/?[a-zA-Z0-9]+/?"
        )
        self.logs_channel = self.client.get_channel(settings.config["channels"]["log"])

    @commands.command(name="automod")
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
    )
    async def automod_edit(self, ctx, arg=None, *words):
        invarg = "Please use the corect arguments\n```!automod add - add word to blacklist\n!automod remove - remove word from blacklist\n!automod blacklist - to see the blacklist```"
        devlogs = self.client.get_channel(settings.config["channels"]["devlog"])
        if arg is None:
            await ctx.send(invarg)
        elif arg == "add":
            with open("resources/blacklist.txt", "a", encoding="utf-8") as f:
                f.write("".join([f"{w}\n" for w in words]))
                await utils.emoji(ctx)
            profanity.load_censor_words_from_file(
                "resources/blacklist.txt", whitelist_words=whitelist
            )
            await devlogs.send(
                f"{utils.timestr}Reloaded `blacklist.txt` and `whitelist.txt` due to edit"
            )
        elif arg == "remove":
            with open("resources/blacklist.txt", "r", encoding="utf-8") as f:
                stored = [w.strip() for w in f.readlines()]
            with open("resources/blacklist.txt", "w", encoding="utf-8") as f:
                f.write("".join([f"{w}\n" for w in stored if w not in words]))
                profanity.load_censor_words_from_file(
                    "resources/blacklist.txt", whitelist_words=whitelist
                )
                await devlogs.send(
                    f"{utils.timestr}Reloaded `blacklist.txt` and `whitelist.txt` due to edit"
                )
            await utils.emoji(ctx)
        elif arg == "blacklist":
            await ctx.send(file=File("resources/blacklist.txt"))
        else:
            await ctx.send(invarg)

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild is None:
            await self.modMail(message)
        elif not await utils.is_staff(message.author):
            await self.websiteBlacklist(message)
            member = await utils.in_roles(
                message.author, settings.config["statusRoles"]["member"]
            )
            await self.spamFilter(message)
            if profanity.contains_profanity(message.content):
                await message.delete()
            elif not member and search(self.url_regex, message.content):
                await message.delete()
            elif search(self.invite_regex, message.content):
                await message.delete()
                await self.logs_channel.send(
                    f"<@{message.author.id}> tried to post:\n{message.content}"
                )

    async def modMail(self, message):
        complaints_channel = self.client.get_channel(
            settings.config["channels"]["complaints"]
        )
        if message.author.id != settings.config["botId"]:
            await complaints_channel.send(
                f"<@{message.author.id}> said: {message.content}"
            )

    async def websiteBlacklist(self, message):
        with open(settings.config["websiteBlacklistFilePath"]) as blocked_file:
            for website in blocked_file:
                website = website.replace("\n", "")
                if website in message.content:
                    dev_chat = self.client.get_channel(
                        settings.config["channels"]["development"]
                    )
                    if message.author.id == settings.config["botId"]:
                        if (
                            message.channel.id
                            != settings.config["channels"]["development"]
                        ):
                            await dev_chat.send(
                                f"{message.author.name} tried to post ```{message.content}```"
                            )
                            break
                    else:
                        await message.delete()
                        staff_chat = self.client.get_channel(
                            settings.config["channels"]["staff-lounge"]
                        )
                        await staff_chat.send(
                            f"{message.author.name} tried to post a link from the blacklist."
                        )
                        break

    async def spamFilter(self, message):
        def _check(m):
            return (
                m.author == message.author
                and len(m.mentions)
                and (datetime.utcnow() - m.created_at).seconds < 15
            )

        if len((list(filter(lambda m: _check(m), self.client.cached_messages)))) >= 5:
            await message.author.add_roles(
                message.guild.get_role(settings.config["statusRoles"]["muted"])
            )
            embed = discord.Embed(
                color=message.author.color, timestamp=message.created_at
            )
            embed.set_author(name="Mute", icon_url=message.author.avatar_url)
            embed.add_field(
                name=f"{message.author} has been Muted! ",
                value="muted for mention spamming",
            )
            await self.logs_channel.send(embed=embed)
            reason = "auto muted for spam pinging"
            await database.mod_event_insert(
                message.author.id,
                3,
                datetime.utcnow(),
                reason,
                settings.config["botId"],
                0,
            )
            await database.userdata_update_query(message.author.id, {"mute": 1})

    @tasks.loop(hours=settings.config["memberUpdateInterval"])
    async def check_member_status(self):

        make_historical_query = text("select id, member_activation_date from userdata")
        results = database.conn.execute(make_historical_query)
        current_guild = self.client.get_guild(settings.config["serverId"])
        for result in results:
            user = current_guild.get_member(result[0])
            if (
                user is not None
                and result[1] != 0
                and (datetime.fromtimestamp(result[1]))
                < datetime.utcnow()
                < (
                    datetime.fromtimestamp(result[1])
                    + timedelta(hours=settings.config["memberUpdateInterval"])
                )
            ):
                member_role = current_guild.get_role(
                    settings.config["statusRoles"]["member"]
                )
                await user.add_roles(member_role)
                await database.mod_event_insert(
                    user.id, 8, datetime.utcnow(), None, settings.config["botId"], 0
                )
                await database.userdata_update_query(user.id, {"member": 1})
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
                before = before_user.display_name + "#" + before_user.discriminator
            if after_user.nick is None:
                after = after_user.display_name + "#" + after_user.discriminator
            await database.name_change_event_insert(after_user.id, before, 2, after)

    @Cog.listener()
    async def on_user_update(self, before_user, after_user):
        if (
            before_user.display_name != after_user.display_name
            or before_user.discriminator != after_user.discriminator
        ):
            before = before_user.display_name + "#" + before_user.discriminator
            after = after_user.display_name + "#" + after_user.discriminator
            await database.name_change_event_insert(after_user.id, before, 1, after)


def setup(client):
    client.add_cog(ModCommands(client))
