import utils
import database

from discord.ext import commands
import discord
import settings
import asyncio
import traceback
import sys
from datetime import datetime, timedelta

def getStreakString(total_streak_length):
    days, remainder = divmod(total_streak_length, 60*60*24)
    hours, remainder = divmod(remainder, 60*60)
    days = int(days)
    hours = int(hours)
    print(days, hours)
    daysStr = f'{days} day{"s" if days > 1 else ""}' if days > 0 else ''
    middleStr = ' and ' if days > 0 and hours > 0 else ''
    hoursStr = f'{hours} hour{"s" if hours != 1 else ""}' if hours > 0 else ''
    return [daysStr, middleStr, hoursStr]

def getOwnedStreakRole(member):
    for role in utils.idData[member.guild.id]['streakRoles']:
        for memberRole in member.roles:
            if memberRole.id == utils.idData[member.guild.id]['streakRoles'][role]:
                return utils.idData[member.guild.id]['streakRoles'][role]
    return None

def getDeservedStreakRole(days, serverID):
    for role in utils.idData[serverID]['streakRoles']:
        if days < int(role) or int(role) == -1:
            return utils.idData[serverID]['streakRoles'][role]

async def updateStreakRole(member, startingDate):
    days = (datetime.today() - startingDate).days
    owned = getOwnedStreakRole(member)
    deserved = getDeservedStreakRole(days, member.guild.id)
    if owned == deserved:
        return
    if owned is not None:
        roleObj = member.guild.get_role(owned)
        await member.remove_roles(roleObj)
    roleObj = member.guild.get_role(deserved)
    await member.add_roles(roleObj)

async def removeStreakRoles(author):
    for role in author.roles:
        id = author.guild.get_role(role.id).id
        if id in settings.config["streakRoles"].values():
            await author.remove_roles(role)
            return


async def check_permitted_streak_set_amount(ctx, number):
    if (number > 30 and not await utils.in_roles(ctx.author, settings.config["statusRoles"]["vip"]) and
            number > 30 and not await utils.in_roles(ctx.author, settings.config["statusRoles"]["boost-vip"])):
        return -1
    elif number > 90 and not await utils.is_staff(ctx):
        return -1
    return number


async def challenge(ctx, role):
    object_role = ctx.guild.get_role(role)
    await ctx.author.remove_roles(object_role)
    no = len(await utils.role_pop(ctx, role))
    if role == settings.config["challenges"]["monthly-challenge-participant"]:
        channel = ctx.guild.get_channel(settings.config["channels"]["monthly-challenge"])
        await channel.send(f'Monthly Challenge members left: {no}')
    elif role == settings.config["challenges"]["yearly-challenge-participant"]:
        channel = ctx.guild.get_channel(settings.config["channels"]["yearly-challenge"])
        await channel.send(f'Yearly Challenge members left: {no}')
    elif role == settings.config["challenges"]["deadpool-participant"]:
        channel = ctx.guild.get_channel(settings.config["channels"]["deadpool-challenge"])
        await channel.send(f'Deadpool memebers left: {no}')


async def delayed_delete(message):
    await asyncio.sleep(5)
    await message.delete()


class Streak(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None


    @commands.command(name="relapse")
    @commands.check(utils.is_in_streak_channel)
    @commands.cooldown(3, 60, commands.BucketType.user)
    async def relapse(self, ctx, *args):
        """resets the users streak to day 0"""

        # Challenges
        Anon = await utils.in_roles(ctx.author, settings.config["modeRoles"]["anon-streak"])
        mChal = await utils.in_roles(ctx.author, settings.config["challenges"]["monthly-challenge-participant"])
        yChal = await utils.in_roles(ctx.author, settings.config["challenges"]["yearly-challenge-participant"])
        dPool = await utils.in_roles(ctx.author, settings.config["challenges"]["deadpool-participant"])
        if Anon:
            await ctx.message.delete()
            await removeStreakRoles(ctx.author)
        if mChal:
            await challenge(ctx, settings.config["challenges"]["monthly-challenge-participant"])
        if yChal:
            await challenge(ctx, settings.config["challenges"]["yearly-challenge-participant"])
        if dPool:
            await challenge(ctx, settings.config["challenges"]["deadpool-participant"])

        # Decodes the args

        maxDays = 365 * 10
        n_days = 0
        n_hours = 0
        if(len(args) > 0 and args[0].isnumeric() and maxDays > int(args[0]) >= 0):
            if (await check_permitted_streak_set_amount(ctx, int(args[0]))) == -1:
                message = await ctx.channel.send('You cannot set your streak this high without moderator help.')
                if Anon:
                    await delayed_delete(message)
                return
            n_days = int(args[0])
            if(len(args) > 1 and args[1].isnumeric() and 24 > int(args[1]) >= 0):
                n_hours = int(args[1])
            elif(len(args) > 1 and (not args[1].isnumeric() or not 24 > int(args[1]) >= 0)):
                message = await ctx.channel.send('The provided command arguments are not permitted.')
                if Anon:
                    await delayed_delete(message)
                return
        elif(len(args) > 0 and (not args[0].isnumeric() or not maxDays > int(args[0]) >= 0)):
            message = await ctx.channel.send('The provided command arguments are not permitted.')
            if Anon:
                await delayed_delete(message)
            return


        # Update userdata table

        current_starting_date = datetime.today() - timedelta(days=n_days, hours=n_hours)
        query = database.userdata.select().where(database.userdata.c.id == ctx.author.id)
        rows = database.conn.execute(query).fetchall()

        if(len(rows)):
            # If they are in the database do this

            if(rows[0]['last_relapse'] is not None):
                # If they have a previous streak do this

                last_starting_date = utils.to_dt(rows[0]['last_relapse'])
                total_streak_length = (current_starting_date - last_starting_date).total_seconds()
                if total_streak_length > 60:
                    [daysStr, middleStr, hoursStr] = getStreakString(total_streak_length)
                    totalHours, _ = divmod(total_streak_length, 60*60)
                    if(rows[0]['past_streaks'] is not None):
                        past_streaks = utils.json.loads(rows[0]['past_streaks'])
                        past_streaks.append(totalHours)
                    else:
                        past_streaks = [totalHours]
                    await database.userdata_update_query(ctx.author.id, {'last_relapse': current_starting_date.timestamp(), 'past_streaks': utils.json.dumps(past_streaks)})
                    message = await ctx.channel.send(f'Your streak was {daysStr}{middleStr}{hoursStr} long.')
                    if not Anon:
                        await updateStreakRole(ctx.author, current_starting_date)
                        await ctx.send('Don’t be dejected')
                        await utils.get_emergency_picture(ctx, relapse=True)
                    if Anon:
                        await delayed_delete(message)

            if(rows[0]['last_relapse'] is None or total_streak_length <= 60):
                # If they dont have a previous streak do this

                await database.userdata_update_query(ctx.author.id, {'last_relapse': current_starting_date.timestamp()})
                if not Anon:
                    await updateStreakRole(ctx.author, current_starting_date)
                message = await ctx.channel.send('Streak set successfully.')
                if Anon:
                    await delayed_delete(message)

        else:
            # If they are not in the database do this

            query = database.userdata.insert().values(id=ctx.author.id,
                    last_relapse=current_starting_date.timestamp())
            database.conn.execute(query)
            if not Anon:
                await updateStreakRole(ctx.author, current_starting_date)
            message = await ctx.channel.send('Streak set successfully.')
            if Anon:
                await delayed_delete(message)

    @relapse.error
    async def relapse_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('That command cannot be used in this channel')
        elif isinstance(error, commands.CommandOnCooldown):
            better_time = await utils.convert_from_seconds(error.retry_after)
            await ctx.send(content=f'This command is on cooldown. Please wait {better_time}', delete_after=5)
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


    @commands.command(name="update")
    @commands.check(utils.is_in_streak_channel)
    @commands.cooldown(3, 900, commands.BucketType.user)
    async def update(self, ctx):
        """updates the users streak"""
        Anon = await utils.in_roles(ctx.author, settings.config["modeRoles"]["anon-streak"])
        if Anon:
            await ctx.message.delete()
            await removeStreakRoles(ctx.author)
        query = database.userdata.select().where(database.userdata.c.id == ctx.author.id)
        rows = database.conn.execute(query).fetchall()
        if(len(rows) and rows[0]['last_relapse'] is not None):
            last_starting_date = utils.to_dt(rows[0]['last_relapse'])
            total_streak_length = (datetime.today() - last_starting_date).total_seconds()
            [daysStr, middleStr, hoursStr] = getStreakString(total_streak_length)
            if not Anon:
                await updateStreakRole(ctx.author, last_starting_date)
            message = await ctx.channel.send(f'Your streak is {daysStr}{middleStr}{hoursStr} long.')
            if Anon:
                await delayed_delete(message)
        else:
            message = await ctx.channel.send("No data about you available do !relapse .")
            if Anon:
                await delayed_delete(message)
    @update.error
    async def update_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('That command cannot be used in this channel')
        elif isinstance(error, commands.CommandOnCooldown):
            better_time = await utils.convert_from_seconds(error.retry_after)
            await ctx.send(content=f'This command is on cooldown. Please wait {better_time}', delete_after=5)
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command(name="fstreak")
    @commands.has_any_role(
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["head-moderator"])
    async def set_streak(self, ctx, member: discord.Member, *args):
        """forces someone's streak to a certain time.

        Takes the same arguments as if you were to set your streak for the first time in relapse.
        second argument must be less than 24 hours, and a user that is already in the database must be provided."""

        if member is None:
            await ctx.channel.send("You need to specify a user.")

        new_starting_date = datetime.today()
        if len(args) >= 1:
            n_days = int(args[0])
            new_starting_date = new_starting_date - timedelta(days=n_days)
        if len(args) >= 2 and int(args[1]) < 24:
            n_hours = int(args[1])
            new_starting_date = new_starting_date - timedelta(hours=n_hours)
        elif len(args) >= 2 and int(args[1]) > 24:
            await ctx.channel.send("Please send a value less than or equal to 24 hours")
            return
        await database.userdata_update_query(member.id, {'last_relapse': new_starting_date.timestamp()})
        await updateStreakRole(ctx.author, new_starting_date)
        await ctx.channel.send("Streak set successfully.")

def setup(client):
    client.add_cog(Streak(client))
