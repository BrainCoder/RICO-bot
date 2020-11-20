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
client.remove_command(help)

#Devlogs setup
today = datetime.now()
ctoday = today.strftime("%d/%m/%Y")
ctime = today.strftime("%H:%M")
timestr = f'**[{ctoday}] [{ctime}] - **'
#/Devlogd setup

#Bot launch
@client.event
async def on_ready():
    print('Bot is active')
    await client.wait_until_ready()
    devlogs = client.get_channel(settings.config["channels"]["devlog"])
    await client.change_presence(status=discord.Status.online, activity=discord.Game('DM me with complaints!'))
    await devlogs.send(f'{timestr}Bot is online')
    await devlogs.send(f'{timestr}Loaded `blacklist.txt` & `whitelist.txt` due to startup')
    await cogs_load()
#/Bot launch

#Cogs
@client.command(name="cog", aliases=["cogs", "c"])
@commands.has_any_role(
    settings.config["statusRoles"]["developer"])
async def cog(ctx, action, extension):
    """Command to manually toggle cogs. For action use either\n**load** - load the cog\n**unload** - unload the cog\n**reload** - reload the cog"""
    devlogs = client.get_channel(settings.config["channels"]["devlog"])
    emoji = '✅'
    log = f'{timestr}`{extension}` {action}ed manually'
    if action == 'load':
        client.load_extension(f'cogs.{extension}')
        await ctx.message.add_reaction(emoji)
        await devlogs.send(log)
    elif action == 'unload':
        client.unload_extension(f'cogs.{extension}')
        await ctx.message.add_reaction(emoji)
        await devlogs.send(log)
    elif action == 'reload':
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f'cogs.{extension}')
        await ctx.message.add_reaction(emoji)
        await devlogs.send(log)

async def cogs_load():
    devlogs = client.get_channel(settings.config["channels"]["devlog"])
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')
            await devlogs.send(f'{timestr}`{filename}` loadeded due to startup')
#/Cogs

#Self destruct
@client.command(name="logout", aliases=["killswitch"])
@commands.has_any_role(
    settings.config["statusRoles"]["admin"])
async def logout(ctx):
    """kills the bot and all its processes"""
    await ctx.send("logging out")
    exit()
#/Self destruct

with open ('token.txt', 'rt') as myfile:
    contents = myfile.read()
    client.run(f'{contents}')