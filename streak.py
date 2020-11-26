import discord
from discord.ext import commands
from discord.ext.commands import cooldown

from utils import idData

import utils
import settings
import asyncio
from datetime import timedelta



intents = discord.Intents.all()
intents.members = True
intents.presences = True
client=commands.Bot(command_prefix='!', intents=intents)

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

@commands.command(name="relapse")
@commands.check(utils.is_in_streak_channel)
@commands.cooldown(1, 60, commands.BucketType.user)
async def relapse(ctx, *args):
    """resets the users streak to day 0"""
    Anon = False
    anon_role = ctx.guild.get_role(settings.config["modeRoles"]["anon-streak"])
    for role in ctx.author.roles:
        if role.id == anon_role.id:
            Anon = True
            await ctx.message.delete()
            await removeStreakRoles(ctx.author)
    members = await ctx.guild.fetch_members(limit=None).flatten()
    for role in ctx.author.roles:
        if role.id == settings.config["statusRoles"]["monthly-challenge-participant"]:
            guild = ctx.guild
            role = guild.get_role(settings.config["statusRoles"]["monthly-challenge-participant"])
            await ctx.author.remove_roles(role)
            partcipants = [m for m in guild.members if role in m.roles]
            no = len(partcipants)
            print(f'{no}')
            channel = guild.get_channel(settings.config["channels"]["monthly-challenge"])
            print(f'{channel}')
            await channel.send(f'Monthly Challenge members left: {no}')
    else:
        maxDays = 365 * 10
        n_days = 0
        n_hours = 0
        if(len(args) > 0 and args[0].isnumeric() and maxDays > int(args[0]) >= 0):
            n_days = int(args[0])
            if(len(args) > 1 and args[1].isnumeric() and 24 > int(args[1]) >= 0):
                n_hours = int(args[1])
            elif(len(args) > 1 and (not args[1].isnumeric() or not 24 > int(args[1]) >= 0)):
                message = await ctx.channel.send(f'The provided command arguments are not permitted.')
                if Anon:
                    await asyncio.sleep(5)
                    await message.delete()
                return
        elif(len(args) > 0 and ( not args[0].isnumeric() or not maxDays > int(args[0]) >= 0)): 
            message = await ctx.channel.send(f'The provided command arguments are not permitted.')
            if Anon:
                await asyncio.sleep(5)
                await message.delete()
            return
        current_starting_date = utils.datetime.today() - timedelta(days=n_days, hours=n_hours)
        query = utils.userdata.select().where(utils.userdata.c.id == ctx.author.id)
        rows = utils.conn.execute(query).fetchall()
        if(len(rows)):
            if(rows[0]['last_relapse'] is not None):
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
                    query = (utils.userdata
                    .update()
                    .where(utils.userdata.c.id == ctx.author.id)
                    .values(last_relapse = current_starting_date.timestamp(),
                            past_streaks = utils.json.dumps(past_streaks)))
                    utils.conn.execute(query)
                    if not Anon:
                        await updateStreakRole(ctx.author, current_starting_date)
                    #pic = await getEmergencyPicture()
                    message = await ctx.channel.send(
                        content=f'Your streak was {daysStr}{middleStr}{hoursStr} long.')#,
                        #file=pic)
                    if Anon:
                        await asyncio.sleep(5)
                        await message.delete()
            if(rows[0]['last_relapse'] is None or total_streak_length <= 60):
                query = (utils.userdata
                .update()
                .where(utils.userdata.c.id == ctx.author.id)
                .values(last_relapse = current_starting_date.timestamp()))
                utils.conn.execute(query)
                if not Anon:
                    await updateStreakRole(ctx.author, current_starting_date)
                message = await ctx.channel.send('Streak set successfully.')
                if Anon:
                    await asyncio.sleep(5)
                    await message.delete()
        else:
            query = utils.userdata.insert().values(id = ctx.author.id,
                    last_relapse = current_starting_date.timestamp())
            utils.conn.execute(query)
            if not Anon:
                await updateStreakRole(ctx.author, current_starting_date)
            message = await ctx.channel.send('Streak set successfully.')
            if Anon:
                await asyncio.sleep(5)
                await message.delete()
@relapse.error
async def relapse_handler(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('That command cannot be used in this channel')


@commands.command(name="update")
@commands.check(utils.is_in_streak_channel)
@commands.cooldown(1, 900, commands.BucketType.user)
async def update(ctx):
    """updates the users streak"""
    Anon = False
    anon_role = ctx.guild.get_role(settings.config["modeRoles"]["anon-streak"])
    for role in ctx.author.roles:
        if role.id == anon_role.id:
            Anon = True
            await ctx.message.delete()
            await removeStreakRoles(ctx.author)
    query = utils.userdata.select().where(utils.userdata.c.id == ctx.author.id)
    rows = utils.conn.execute(query).fetchall()
    if(len(rows) and rows[0]['last_relapse'] is not None):
        last_starting_date = utils.to_dt(rows[0]['last_relapse'])
        total_streak_length = (utils.datetime.today() - last_starting_date).total_seconds()
        [daysStr, middleStr, hoursStr] = getStreakString(total_streak_length)
        if not Anon:
            await updateStreakRole(ctx.author, last_starting_date)
        message = await ctx.channel.send(f'Your streak is {daysStr}{middleStr}{hoursStr} long.')
        if Anon:
            await asyncio.sleep(5)
            await message.delete()
    else:
        message = await ctx.channel.send("No data about you available do !relapse .")
        if Anon:
            await asyncio.sleep(5)
            await message.delete()
@update.error
async def update_handler(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('That command cannot be used in this channel')

def getOwnedStreakRole(member):
    for role in idData[member.guild.id]['streakRoles']:
        for memberRole in member.roles:
            if memberRole.id == idData[member.guild.id]['streakRoles'][role]:
                return idData[member.guild.id]['streakRoles'][role]
    return None

def getDeservedStreakRole(days, serverID):
    for role in idData[serverID]['streakRoles']:
        if days < int(role) or int(role) == -1:
            return idData[serverID]['streakRoles'][role]

async def updateStreakRole(member, startingDate):
    days = (utils.datetime.today() - startingDate).days
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
