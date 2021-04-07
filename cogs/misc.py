import utils
import database
from resources.langauges import lang_dict

import discord
from discord.ext import commands
from discord.ext.commands import cooldown

from datetime import datetime, timedelta
import random
import settings
import asyncio
import sys
import http.client
import json

from sqlalchemy import text


class Extra(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.authkey = sys.argv[4]

    async def prepare_string(self, query):
        if len(query) > 1:
            return query.replace(" ", "%20")
        else:
            return query

    @commands.command(name="selfmute")
    @cooldown(1, 60, commands.BucketType.user)
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
        settings.config["statusRoles"]["vip"],
        settings.config["statusRoles"]["boost-vip"],
        settings.config["statusRoles"]["member"],
    )
    async def selfmute(self, ctx):
        """Command that stops the user from being able to talk in majority of channels"""
        selfmute_role = ctx.guild.get_role(settings.config["statusRoles"]["self-mute"])
        if await utils.in_roles(ctx.author, selfmute_role.id):
            await ctx.author.remove_roles(selfmute_role)
        else:
            await ctx.author.add_roles(selfmute_role)
        await utils.emoji(ctx)

    @commands.command(name="urban", aliases=["urb", "define", "def"])
    @cooldown(1, 60, commands.BucketType.user)
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
        settings.config["statusRoles"]["vip"],
        settings.config["statusRoles"]["boost-vip"],
        settings.config["statusRoles"]["member"],
    )
    async def urban(self, ctx, *, query):
        """standard urban dictionary command"""

        nquery = await self.prepare_string(query)
        conn = http.client.HTTPSConnection(
            "mashape-community-urban-dictionary.p.rapidapi.com"
        )
        headers = {
            "x-rapidapi-key": self.authkey,
            "x-rapidapi-host": "mashape-community-urban-dictionary.p.rapidapi.com",
        }
        conn.request("GET", f"/define?term={nquery}", headers=headers)
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        try:
            first_def = data["list"][0]
        except IndexError:
            await ctx.send("Sorry, i couldnt find anything")
            return
        message = f"**{first_def['word']}:**\n{first_def['definition']}\n\n*example:\n{first_def['example']}*\n(<{first_def['permalink']}>)"
        await ctx.send(message)

    @commands.command(name="translate", aliases=["tran"])
    @cooldown(1, 60)
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
        settings.config["statusRoles"]["vip"],
        settings.config["statusRoles"]["boost-vip"],
        settings.config["statusRoles"]["member"],
    )
    async def translate(self, ctx, langauge, *, query):
        """standard translation command"""
        if query is None:
            await ctx.send(
                "Please specify the langauge you want to translate to. For more information please do `!help translate"
            )
            return
        endpoint = None
        for entry in lang_dict:
            if langauge.lower() == entry:
                endpoint = lang_dict[entry]
                break
        if endpoint is None:
            await ctx.send("That is not a valid language")
            return
        nquery = await self.prepare_string(query)
        conn = http.client.HTTPSConnection("google-translate1.p.rapidapi.com")
        payload = f"q={nquery}&source=en&target={endpoint}"
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "accept-encoding": "application/gzip",
            "x-rapidapi-key": self.authkey,
            "x-rapidapi-host": "google-translate1.p.rapidapi.com",
        }
        conn.request("POST", "/language/translate/v2", payload, headers)
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        translation = data["data"]["translations"][0]["translatedText"]
        await ctx.send(translation)

    @commands.command(name="8ball", aliases=["8b"])
    @cooldown(1, 60, commands.BucketType.user)
    async def _8ball(self, ctx, *, question):
        """standard 8ball command"""
        responses = [
            "It is certain",
            "It is decidedly so",
            "Yes Definatley",
            "You may rely on it",
            "As I se it, yes",
            "Most Likely",
            "Outlook good",
            "Yes.",
            "Signs point to yes",
            "Reply hazy, try again",
            "Ask again later",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",
            "Dont count on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful",
        ]
        if "@everyone" in question or "@here" in question:
            await utils.emoji(ctx, "❌")
        else:
            await ctx.send(
                f" **Question:** {question}\n**Answer:** {random.choice(responses)}"
            )

    @commands.command(name="dosomething")
    async def dosomething(self, ctx):
        """try it and find out ;)"""
        await ctx.channel.send("*Does your mum*")

    @commands.command(name="userinfo", aliases=["ui"])
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
        settings.config["statusRoles"]["vip"],
        settings.config["statusRoles"]["boost-vip"],
        settings.config["statusRoles"]["member"],
    )
    async def ui(self, ctx, *, member: discord.Member = None):
        """gives basic info on the user tagged in the arg"""
        if member is None:
            member = ctx.author
        member_joined_at = member.joined_at.strftime("%A, %B %d %Y at %H:%M:%S %p")
        df = await database.userdata_select_query(member.id, False)
        if df and df["member_activation_date"] != 0:
            member_joined_at = (
                datetime.fromtimestamp(df["member_activation_date"])
                - timedelta(hours=settings.config["memberUpdateInterval"])
            ).strftime("%A, %B %d %Y at %H:%M:%S %p")
        usernames = await self.build_username_list(member)
        date_created = member.created_at.strftime("%A, %B %d %Y at %H:%M:%S %p")
        user_avatar_url = member.avatar_url
        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_author(name="UI", icon_url=user_avatar_url)
        embed.add_field(name="Account was created at: ", value=f"{date_created}.")
        embed.add_field(name="Member joined at: ", value=f"{member_joined_at}.")
        embed.add_field(name="Previous Usernames: ", value=usernames)
        await ctx.send(embed=embed)

    @commands.command(name="avatar", aliases=["av"])
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
        settings.config["statusRoles"]["vip"],
        settings.config["statusRoles"]["boost-vip"],
        settings.config["statusRoles"]["member"],
    )
    async def avatar(self, ctx, *, avamember: discord.Member = None):
        """sends a link of the users avatar"""
        if avamember is None:
            userAvatarUrl = ctx.author.avatar_url
            await ctx.send(f"<@{ctx.author.id}>s avatar is:\n{userAvatarUrl}")
        else:
            userAvatarUrl = avamember.avatar_url
            await ctx.send(f"<@{avamember.id}>s avatar is:\n{userAvatarUrl}")

    @commands.command(name="gfsandwich")
    async def gfsandwich(self, ctx):
        """Evidence that the bot is hounds gf"""
        hound = await utils.in_roles(
            ctx.author, settings.config["staffRoles"]["head-dev"]
        )
        if not hound:
            await ctx.send("Ur not my dad :c")
        else:
            await ctx.send(
                "uwu what kinda of sandwich does daddy want =^.^=", delete_after=5
            )

    @commands.command(name="remind", aliases=["remindme"])
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
        settings.config["statusRoles"]["vip"],
        settings.config["statusRoles"]["boost-vip"],
        settings.config["statusRoles"]["member"],
    )
    async def remind(self, ctx, *, time: utils.TimeConverter = None):
        """Will ping the user after a specific amount of time in the channel the reminder was sent in."""
        if time is None:
            await ctx.send("Please specify the timer", delete_after=5)
        else:
            await utils.emoji(ctx)
            await asyncio.sleep(time)
            await ctx.send(f"{ctx.author.mention}")

    @commands.command(name="emergency", aliases=["m"])
    async def emergency(self, ctx):
        """Gets an emergency link from emergency.nofap.com website."""
        await utils.get_emergency_picture(ctx)

    @commands.command(name="tip", aliases=["t"])
    async def tip(self, ctx):
        tips = await utils.extract_data("resources/tips.txt")
        await ctx.send(f"{random.choice(tips)}")

    async def build_username_list(self, member):
        with database.engine.connect() as connection:
            username_query = text(
                "select * from np_db.name_change_event where user_id = "
                + str(member.id)
                + " and np_db.name_change_event.previous_name not like '[AFK]%' and "
                "np_db.name_change_event.new_name not like '[AFK]%'"
            )
            result = connection.execute(username_query).fetchall()
            if result:
                # This is used to determine how many usernames are allowed to be in the list.
                # Increase or decrease to your liking
                max_length = 5
                # Track the amount of times the loop has executed
                # while the incrementer worries about going through the results
                length_tracker = 0
                name_list = ""
                unique_names = []

                # If they have more than 5 name changes, the assumption is that they're a frequent name changer,
                # and so a larger range of names are looked at.
                incrementing_amount = 1
                if len(result) > 5:
                    incrementing_amount = 5

                for i in range(0, len(result), incrementing_amount):
                    if result[i][2] not in unique_names:
                        unique_names.append(result[i][2])
                        name_list += result[i][2] + "\n"
                        length_tracker = length_tracker + 1
                        if length_tracker > max_length:
                            break
                return name_list[:-1]
            else:
                return "No previous usernames have been saved in the database."


def setup(client):
    client.add_cog(Extra(client))
