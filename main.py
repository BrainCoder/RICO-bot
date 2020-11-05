import discord
from discord.ext import commands, tasks
import os
import sys
import settings
from datetime import datetime

import utils
from streak import relapse
from streak import update

if len(sys.argv) < 3:
    print("Need config file and database url in order to run. Example: python config.json "
          "mysql+pymysql://user(:password if present)@localhost/database_name")
    sys.exit(0)

with open (sys.argv[1], 'rt') as conf_file:
    settings.init()
    settings.config = utils.json.load(conf_file)
    settings.config["databaseUrl"] = sys.argv[2]
    utils.init()

intents = discord.Intents.all()
intents.members = True
intents.presences = True
client=commands.Bot(command_prefix='!', intents=intents)
mCount = 0

client.add_command(relapse)
client.add_command(update)
client.remove_command('help')

#Cogs
@client.command(name="load")
@commands.has_any_role(
    settings.config["statusRoles"]["developer"])
async def load(ctx, extension):
    """loads the identified cog"""
    client.load_extension(f'cogs.{extension}')
    emoji = '✅'
    await ctx.message.add_reaction(emoji)

@client.command(name="unload")
@commands.has_any_role(
    settings.config["statusRoles"]["developer"])
async def unload(ctx, extension):
    """unloads the identified cog"""
    client.unload_extension(f'cogs.{extension}')
    emoji = '✅'
    await ctx.message.add_reaction(emoji)

@client.command(name="reload")
@commands.has_any_role(
    settings.config["statusRoles"]["developer"])
async def reload(ctx, extension):
    """reloads the identified cog"""
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    emoji = '✅'
    await ctx.message.add_reaction(emoji)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
#/Cogs

#Devlogs setup
today = datetime.now()
ctoday = today.strftime("%d/%m/%Y")
ctime = today.strftime("%H:%M")
timestr = f'**[{ctoday}] [{ctime}] -**'
#Devlogs setup

#Member count plus game status
@tasks.loop(minutes = 15)
async def mcount_update():
    for guild in client.guilds:
        if guild.id != settings.config["serverId"]:
            continue
        mCount = guild.member_count
        channel = client.get_channel(settings.config["channels"]["memberscount"])
        break
    print(f'There are now {mCount} members of this server')
    await channel.edit(name=(f'[{mCount} members]'))

@client.event
async def on_ready():
    devlogs = client.get_channel(settings.config["channels"]["devlog"])
    print('Bot is active')
    mcount_update.start()
    await client.change_presence(status=discord.Status.online, activity=discord.Game('DM me with complaints!'))
    await devlogs.send(f'{timestr}Bot is online')
    await devlogs.send(f'{timestr}Loaded `blacklist.txt` & `whitelist.txt` due to startup')
#/Member count plus game status

#Welcome message

@client.event
async def on_member_join(member):
    channel = client.get_channel(settings.config["channels"]["welcome"])
    await channel.send(f'{member.mention} welcome! Please go to <#519455164894019584> to read an overview of what this server is about. Go to <#767871942056869938> and <#767742624739622932> to see the commands that you can use to assign yourself.')
    verify_previous_query = utils.userdata.select().where(utils.userdata.c.id == member.id)
    result = utils.conn.execute(verify_previous_query).fetchone()
    if not result:
        query = utils.userdata.insert(). \
            values(id=member.id)
        utils.conn.execute(query)

#/Welcome message

#Complaints DM code & Word Filter

@client.event
async def on_message(message):
    channel = client.get_channel(settings.config["channels"]["complaints"])     #-- Complaints part starts here
    if message.guild is None and message.author != client.user:
        await channel.send(f"<@{message.author.id}> said: {message.content}")
    await client.process_commands(message)

@client.command(name="dm", aliases=['message'], checks=[utils.is_in_complaint_channel()])
async def dm(ctx, member: discord.Member, *, content):
    """messages the given user through the bot"""
    channel = await member.create_dm()
    await channel.send(content)
    emoji = '✅'
    await ctx.message.add_reaction(emoji)

#/Complaints DM code & Word filter

#Self destruct
@client.command(name="logout", aliases=["killswitch"])
@commands.has_any_role(
    settings.config["statusRoles"]["admin"],
    settings.config["statusRoles"]["developer"])
async def logout(ctx):
    """kills the bot and all its processes"""
    await ctx.message.delete()
    await ctx.send("logging out")
    exit()
#/Self destruct
"""
async def monthStart():
    while True:
        now = datetime.today()
        y = now.year if now.month < 12 else now.year+1
        m = (now.month+1) if now.month < 12 else 1
        secondsToSleep = (datetime(y, m, 1) - datetime.today()).total_seconds()
        channel = client.get_channel(582650072672632833)
        await asyncio.sleep(secondsToSleep)
        await startChallenge()
"""
"""
async def hourly():
    while True:
        await asyncio.sleep(60*60)
        for key in banDict:
            if banDict[key] > 0:
                banDict[key] -= 1
            else:
                del banDict[key]
"""

#async def hourly():
#    while True:
#        await asyncio.sleep(60*60)
#        for key in banDict:
#            if banDict[key] > 0:
#                banDict[key] -= 1
#            else:
#                del banDict[key]


#@client.event
#async def on_command_error(ctx, error):
#    if isinstance(error, CommandNotFound) or isinstance(error, CheckFailure):
#        return
#    raise error

with open ('token.txt', 'rt') as myfile:
    contents = myfile.read()
    client.run(f'{contents}')
