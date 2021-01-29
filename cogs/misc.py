import utils
import database

import discord
from discord.ext import commands
from discord.ext.commands import cooldown, Cog

from datetime import datetime, timedelta
import random
import settings
import asyncio
import nest_asyncio

from sqlalchemy import text


class Extra(commands.Cog):

    def __init__(self, client):
        nest_asyncio.apply()
        self.client = client
        self.afk_users = []
        rows = asyncio.run(database.userdata_select_query())
        for row in rows:
            if row[12] == 1:
                self.afk_users.append(row[0])


    @commands.command(name="8ball", aliases=['8b'])
    @cooldown(1, 60)
    async def _8ball(self, ctx, *, question):
        """standard 8ball command"""
        responses = [
            'It is certain',
            'It is decidedly so',
            'Yes Definatley',
            'You may rely on it',
            'As I se it, yes',
            'Most Likely',
            'Outlook good',
            'Yes.',
            'Signs point to yes',
            'Reply hazy, try again',
            'Ask again later',
            'Better not tell you now',
            'Cannot predict now',
            'Concentrate and ask again',
            'Dont count on it',
            'My reply is no',
            'My sources say no',
            'Outlook not so good',
            'Very doubtful']
        if '@everyone' in question or '@here' in question:
            await utils.emoji(ctx, '❌')
        else:
            await ctx.send(f' **Question:** {question}\n**Answer:** {random.choice(responses)}')


    @commands.command(name="dosomething")
    async def dosomething(self, ctx):
        """try it and find out ;)"""
        await ctx.channel.send("*Does your mum*")


    @commands.command(name="userinfo", aliases=["ui"])
    @commands.has_any_role(
        settings.config["statusRoles"]["vip"],
        settings.config["statusRoles"]["boost-vip"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"])
    async def ui(self, ctx, *, member: discord.Member = None):
        """gives basic info on the user tagged in the arg"""
        if member is None:
            member = ctx.author
        member_joined_at = member.joined_at.strftime("%A, %B %d %Y at %H:%M:%S %p")
        result = await database.userdata_select_query(member.id, False)
        if result and result[12] != 0:
            member_joined_at = (datetime.fromtimestamp(result[12]) -
                                timedelta(hours=settings.config["memberUpdateInterval"])) \
                .strftime("%A, %B %d %Y at %H:%M:%S %p")
        usernames = await self.build_username_list(member)
        date_created = member.created_at.strftime("%A, %B %d %Y at %H:%M:%S %p")
        user_avatar_url = member.avatar_url
        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_author(name="UI", icon_url=user_avatar_url)
        embed.add_field(name='Account was created at: ', value=f"{date_created}.")
        embed.add_field(name="Member joined at: ", value=f"{member_joined_at}.")
        embed.add_field(name="Previous Usernames: ", value=usernames)
        await ctx.send(embed=embed)


    @commands.command(name="avatar", aliases=["av"])
    @commands.has_any_role(
        settings.config["statusRoles"]["vip"],
        settings.config["statusRoles"]["boost-vip"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"])
    async def avatar(self, ctx, *, avamember: discord.Member = None):
        """sends a link of the users avatar"""
        if avamember is None:
            userAvatarUrl = ctx.author.avatar_url
            await ctx.send(f'<@{ctx.author.id}>s avatar is:\n{userAvatarUrl}')
        else:
            userAvatarUrl = avamember.avatar_url
            await ctx.send(f"<@{avamember.id}>s avatar is:\n{userAvatarUrl}")


    @commands.command(name="gfsandwich")
    async def gfsandwich(self, ctx):
        """Evidence that the bot is hounds gf"""
        hound = await utils.in_roles(ctx.author, settings.config["staffRoles"]["head-dev"])
        if not hound:
            await ctx.send('Ur not my dad :c')
        else:
            await ctx.send('uwu what kinda of sandwich does daddy want =^.^=', delete_after=5)


    @commands.command(name="remind", aliases=["remindme"])
    @commands.has_any_role(
        settings.config["statusRoles"]["member"])
    async def remind(self, ctx, *, time: utils.TimeConverter = None):
        """unmute the user"""
        if time is None:
            await ctx.send('Please specify the timer', delete_after=5)
        else:
            await utils.emoji(ctx)
            await asyncio.sleep(time)
            await ctx.send(f'{ctx.author.mention}')


    @commands.command(name="emergency", aliases=['m'])
    async def emergency(self, ctx):
        """Gets an emergency link from emergency.nofap.com website."""
        await utils.get_emergency_picture(ctx)


    @commands.command(name="tip", aliases=["t"])
    async def tip(self, ctx):
        tips = await utils.extract_data('resources/tips.txt')
        await ctx.send(f'{random.choice(tips)}')


    async def build_username_list(self, member):
        with database.engine.connect() as connection:
            username_query = text(f'select * from np_db.name_change_event where user_id = {member.id}')
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


    @commands.command(name='afk')
    async def afk(self, ctx, *, message: str = None):
        nickname = 0
        if ctx.author.name != ctx.author.display_name:
            nickname = 1
        await database.userdata_update_query(ctx.author.id, {'afk': 1})
        await database.afk_event_insert(ctx.author.id, ctx.author.display_name, nickname, message)
        self.afk_users.append(ctx.author.id)
        await ctx.author.edit(nick=f'[AFK] {ctx.author.display_name}')
        await utils.emoji(ctx)


    @Cog.listener()
    async def on_message(self, message):
        if not await utils.in_roles(message.author, settings.config["statusRoles"]["bot-role"]):

            # Check if user is afk
            if message.author.id in self.afk_users and "!afk" not in message.content:

                # If is isnt in a staff channel
                if not await utils.in_staff_channel(message.channel.id):

                    # Edit the userdata table
                    await database.userdata_update_query(message.author.id, {'afk': 0})

                    # Revert nickname change
                    rows = await database.afk_event_select(message.author.id)
                    print(rows)
                    if rows[4] == 1:
                        await message.author.edit(nick=rows[3])
                    else:
                        await message.author.edit(nick=None)

                    # Rebuild username list
                    self.afk_users = await self.build_afk_list()

                    # Notify the user they are no longer AFK
                    await database.afk_event_update(message.author.id)
                    await message.channel.send(f'{message.author.mention} you are no longer afk')

            else:

                # Check if the message has a mention in it
                if len(message.mentions) > 0:

                    # Parse through the mentions
                    for mention in message.mentions:

                        # If the user is in the afk_users list
                        if mention.id in self.afk_users:

                            # Get the message from the databse
                            row = await database.afk_event_select(mention.id, True)
                            afk_message = row[2]

                            # If no message
                            if message is None:
                                await message.channel.send(f'{mention.id} is currently AFK')

                            # If message
                            else:
                                await message.channel.send(f'{mention.id} is currently afk with the message "{afk_message}"')


def setup(client):
    client.add_cog(Extra(client))
