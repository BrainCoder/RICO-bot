from streak import *
from discord.ext import commands
import discord
import os
import sys
import settings
import threading

intents = discord.Intents.all()
intents.members = True
intents.presences = True
client=commands.Bot(command_prefix='!', intents=intents)
mCount = 0
client.add_command(reset)
client.add_command(relapse)
client.add_command(update)

#Cogs
@client.command()
@commands.has_permissions(ban_members=True)
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'loaded {extension}')

@client.command()
@commands.has_permissions(ban_members=True)
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'unloaded {extension}')

@client.command()
@commands.has_permissions(ban_members=True)
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'reloaded {extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
#/Cogs

#Member count plus game status
async def mCount_update():
    threading.Timer(1800, mCount_update).start()
    for guild in client.guilds:
        if guild.id != settings.config["serverId"]:
            continue
        mCount = guild.member_count
        channel = client.get_channel(settings.config["channels"]["memberscount"])
        break
    print(f'There are now {mCount} mebers of this server')
    await channel.edit(name=(f'{mCount} members'))

@client.event
async def on_ready():
    print('Bot is active')
    await mCount_update()
    await client.change_presence(status=discord.Status.online, activity=discord.Game('DM me with complaints!'))
#/Member count plus game status

#Welcome message

@client.event
async def on_member_join(member):
    channel = client.get_channel(settings.config["channels"]["welcome"])
    await channel.send(f'{member.mention} welcome! Please go to <#519455164894019584> to read an overview of what this server is about. Go to <#519627611836776490> and <#567283111273037834> to see the commands that you can use to assign yourself.')

#/Welcome message

#Complaints DM code & Word Filter

@client.event
async def on_message(message):
    with open ('badWords.txt', 'r') as file:
        content = file.read()
    badWordsArr = content.split(',\n')
    for word in badWordsArr:
        if word in message.content.lower():
            await message.delete()
            #TODO: Warn/mute the user here
            break
    channel = client.get_channel(settings.config["channels"]["complaints"])     #-- Complaints part starts here
    if message.guild is None and message.author != client.user:
        await channel.send(f"<@{message.author.id}> said: {message.content}")
    await client.process_commands(message)

@client.command(checks=[is_in_channel2()])
async def dm(ctx, member: discord.Member, *, content):
    channel = await member.create_dm()
    await channel.send(content)

#/Complaints DM code & Word filter

#Self destruct
@client.command()
@commands.has_permissions(administrator=True)
async def logout(ctx):
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

if (len(sys.argv) < 2):
    print("Need config file in order to run. enter an argument to run. Example: python config.json")
else:
    with open (sys.argv[1], 'rt') as conf_file:
        settings.init()
        settings.config = json.load(conf_file)
    with open ('token.txt', 'rt') as myfile:
        contents = myfile.read()
        client.run(f'{contents}')
