import utils
import database

import discord
from discord.ext import commands

import os
import sys
import settings

if len(sys.argv) < 5:
    print("\nArgs entered incorrectly, please refer to the args wikipage:\n"
        "https://gitlab.com/HellHound0066/noporn-companion/-/wikis/Required-Arguments\n")
    sys.exit(0)

with open(sys.argv[1], 'rt') as conf_file:
    settings.init()
    settings.config = utils.json.load(conf_file)
    settings.config["databaseUrl"] = sys.argv[2]
    database.init()

intents = discord.Intents.all()
intents.members = True
intents.presences = True
client = commands.Bot(command_prefix=settings.config["prefix"], intents=intents, case_insensitive=True)

@client.event
async def on_ready():
    print('Bot is active')
    await client.wait_until_ready()
    devlogs = client.get_channel(settings.config["channels"]["devlog"])
    if settings.config["prefix"] == '!':
        await devlogs.send('---')
        await devlogs.send(f'{utils.timestr}Bot is online')
        await devlogs.send(f'{utils.timestr}Loaded `blacklist.txt` & `whitelist.txt` due to startup')
    await cogs_load()

async def cogs_load():
    if settings.config["prefix"] == '!':
        devlogs = client.get_channel(settings.config["channels"]["devlog"])
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                client.load_extension(f'cogs.{filename[:-3]}')
                await devlogs.send(f'{utils.timestr}`{filename}` loadeded due to startup')
                print(f'loaded {filename}')
        await devlogs.send(f'{utils.timestr}**all cogs loaded**')
        print('all cogs loaded')
    else:
        client.load_extension('cogs.developer')
        client.load_extension('cogs.errors')

@client.command(name="logout", aliases=["killswitch"])
@commands.has_any_role(
    settings.config["staffRoles"]["admin"])
async def logout(ctx):
    """kills the bot and all its processes"""
    await ctx.send("logging out")
    exit()

@client.command(name="creset")
@commands.has_any_role(
    settings.config["staffRoles"]["developer"])
async def creset(ctx):
    devlogs = client.get_channel(settings.config["channels"]["devlog"])
    log = f'{utils.timestr}`cogs` loaded manually using !creset command'
    client.load_extension('cogs.developer')
    await utils.emoji(ctx)
    if settings.config["prefix"] == '!':
        await devlogs.send(log)

client.run(sys.argv[4])
