import aiohttp
from PIL import Image
import io
from utils import *
import discord

client=commands.Bot(command_prefix='!')

def create_table():
    meta.create_all(engine)
#create_table()
async def insert_data():
    ins = userdata.insert().values(id = 488779608172658690,
                                  # last_relapse = 12345678912345678,
                                   usertype = 0,
                                   past_streaks = json.dumps([56,15,74]),
                                   points = 5)
    conn.execute(ins)
#insert_data()
#d = userdata.select()
#rows = conn.execute(d)
#print([row for row in rows])
#query = userdata.select().where(userdata.c.id == 488779608172658690)
#rows = conn.execute(query).fetchall()
#print(rows)
#exit()

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

@commands.command(checks=[is_in_channel()])
async def reset(ctx, *args):
    query = (userdata
    .delete()
    .where(userdata.c.id == ctx.author.id))
    conn.execute(query)

async def remove_role(member):
    role = discord.utils.get(ctx.guild.roles, name='M-Challenge_Participant')
    await member.remove_roles(role)

@commands.command(checks=[is_in_channel()])
async def relapse(ctx, *args):
<<<<<<< HEAD
#    members = await ctx.guild.fetch_members(limit=None).flatten()
#    for role in ctx.author.roles:
#        if role.id == 582640858378272793:
#            signupRole = ctx.guild.get_role(582640858378272793)
#            await ctx.author.remove_roles(signupRole)
#            newParticipants = []
#            for discord.guild in client.guilds:
#                members = await discord.guild.fetch_members(limit=None).flatten()
#                for member in members:
#                    for role in member.roles:
#                        if role.id == 582640858378272793:  # MonthlyChallenge-participant
#                            if (newParticipants.append(member) != None):
#                                newParticipants.append(member)
#                                break
#            channel = client.get_channel(582650072672632833)
#            await channel.send(f"Monthly Challenge Members Left: {len(newParticipants)}")
#            print(len(newParticipants))
#    else:
=======
    members = await ctx.guild.fetch_members(limit=None).flatten()
    for role in ctx.author.roles:
        if role.id == 582640858378272793:
            signupRole = ctx.guild.get_role(582640858378272793)
            await ctx.author.remove_roles(signupRole)
            newParticipants = []
            for discord.guild in client.guilds:
                members = await discord.guild.fetch_members(limit=None).flatten()
                for member in members:
                    for role in member.roles:
                        if role.id == 582640858378272793:  # MonthlyChallenge-participant
                            if (newParticipants.append(member) != None):
                                newParticipants.append(member)
                                break
            channel = client.get_channel(582650072672632833)
            await channel.send(f"Monthly Challenge Members Left: {len(newParticipants)}")
            print(len(newParticipants))
    else:
>>>>>>> 979d04e174d028e4b8dbad31425260d46f760e17
        role = discord.utils.get(ctx.guild.roles, name='M-Challenge_Participant')
        await ctx.author.remove_roles(role)
        maxDays = 365 * 10
        n_days = 0
        n_hours = 0
        if(len(args) > 0 and args[0].isnumeric() and maxDays > int(args[0]) >= 0):
            n_days = int(args[0])
            if(len(args) > 1 and args[1].isnumeric() and 24 > int(args[1]) >= 0):
                n_hours = int(args[1])
            elif(len(args) > 1 and (not args[1].isnumeric() or not 24 > int(args[1]) >= 0)):
                await ctx.channel.send(f'The provided command arguments are not permitted.')
                return
        elif(len(args) > 0 and ( not args[0].isnumeric() or not maxDays > int(args[0]) >= 0)):
            await ctx.channel.send(f'The provided command arguments are not permitted.')
            return
        current_starting_date = datetime.today() - timedelta(days=n_days, hours=n_hours)
        query = userdata.select().where(userdata.c.id == ctx.author.id)
        rows = conn.execute(query).fetchall()
        if(len(rows)):
            if(rows[0]['last_relapse'] is not None):
                last_starting_date = to_dt(rows[0]['last_relapse'])
                total_streak_length = (current_starting_date - last_starting_date).total_seconds()
                if total_streak_length > 60:
                    [daysStr, middleStr, hoursStr] = getStreakString(total_streak_length)
                    totalHours, _ = divmod(total_streak_length, 60*60)
                    if(rows[0]['past_streaks'] is not None):
                        past_streaks = json.loads(rows[0]['past_streaks'])
                        past_streaks.append(totalHours)
                    else:
                        past_streaks = [totalHours]
                    query = (userdata
                    .update()
                    .where(userdata.c.id == ctx.author.id)
                    .values(last_relapse = current_starting_date.timestamp(),
                            past_streaks = json.dumps(past_streaks)))
                    conn.execute(query)
                    await updateStreakRole(ctx.author, current_starting_date)
                    #pic = await getEmergencyPicture()
                    await ctx.channel.send(
                        content=f'Your streak was {daysStr}{middleStr}{hoursStr} long.')#,
                        #file=pic)
            if(rows[0]['last_relapse'] is None or total_streak_length <= 60):
                query = (userdata
                .update()
                .where(userdata.c.id == ctx.author.id)
                .values(last_relapse = current_starting_date.timestamp()))
                conn.execute(query)
                await updateStreakRole(ctx.author, current_starting_date)
                await ctx.channel.send('Streak set successfully.')
        else:
            query = userdata.insert().values(id = ctx.author.id,
                    last_relapse = current_starting_date.timestamp())
            conn.execute(query)
            await updateStreakRole(ctx.author, current_starting_date)
            await ctx.channel.send('Streak set successfully.')


@commands.command(checks=[is_in_channel()])
async def update(ctx):
    query = userdata.select().where(userdata.c.id == ctx.author.id)
    rows = conn.execute(query).fetchall()
    if(len(rows) and rows[0]['last_relapse'] is not None):
        last_starting_date = to_dt(rows[0]['last_relapse'])
        total_streak_length = (datetime.today() - last_starting_date).total_seconds()
        [daysStr, middleStr, hoursStr] = getStreakString(total_streak_length)
        await updateStreakRole(ctx.author, last_starting_date)
        await ctx.channel.send(f'Your streak is {daysStr}{middleStr}{hoursStr} long.')
    else:
        await ctx.channel.send("No data about you available do !relapse .")

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





url = "https://emergency.nofap.com/director.php?cat=em&religious=false"
async def getEmergencyPicture():
    async with aiohttp.ClientSession() as cs:
        async with cs.get(url) as response:
            #res = await r.json()  # returns dict
            #await ctx.send(res['slideshow']['author'])
            print(response.content)
            result = await response.read()
            print(response)
    #response = requests.get(url).content
    #img = BytesIO(response.content) #Image.open(
            r = discord.File(io.BytesIO(result),filename="pic"+url[-4:])
            return r
#ioloop = asyncio.get_event_loop()
#ioloop.run_until_complete(getEmergencyPicture())
