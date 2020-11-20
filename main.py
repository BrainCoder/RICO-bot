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

with open ('token.txt', 'rt') as myfile:
    contents = myfile.read()
    client.run(f'{contents}')
