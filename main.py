import utils
import database

import discord
from discord.ext import commands

import os
import sys
import settings

if len(sys.argv) < 4:
    print(
        "\nArgs entered incorrectly, please refer to the args wikipage:\n"
        "https://gitlab.com/HellHound0066/noporn-companion/-/wikis/Required-Arguments\n"
    )
    sys.exit(0)

with open(sys.argv[1], "rt") as conf_file:
    settings.init()
    settings.config = utils.json.load(conf_file)
    settings.config["databaseUrl"] = sys.argv[2]
    database.init()

intents = discord.Intents.all()
intents.members = True
intents.presences = True
client = commands.Bot(
    command_prefix=settings.config["prefix"], intents=intents, case_insensitive=True
)


@client.event
async def on_ready():
    print("Bot is active")
    await client.wait_until_ready()
    devlogs = client.get_channel(settings.config["channels"]["devlog"])
    await devlogs.send("---")
    await devlogs.send(f"{utils.timestr}Bot is online")
    await devlogs.send(
        f"{utils.timestr}Loaded `blacklist.txt` & `whitelist.txt` due to startup"
    )
    await cogs_load()


async def cogs_load():
    devlogs = client.get_channel(settings.config["channels"]["devlog"])
    cogs = ["automod", "background", "challenge", "developer", "errors", "help", "misc", "moderation", "moderator", "streak", "suggestion", "welcome"]

    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            if filename[:-3] in cogs:
                client.load_extension(f"cogs.{filename[:-3]}")
                await devlogs.send(f"{utils.timestr}`{filename}` loaded due to startup")
                print(f"loaded {filename}")

    await devlogs.send(f"{utils.timestr}**all cogs loaded**")
    print("all cogs loaded")


@client.command(name="logout", aliases=["killswitch"])
@commands.has_any_role(settings.config["staffRoles"]["admin"])
async def logout(ctx):
    """kills the bot and all its processes"""
    await ctx.send("logging out")
    exit()


@client.command(name="creset")
@commands.has_any_role(
    settings.config["staffRoles"]["head-dev"],
    settings.config["staffRoles"]["developer"],
)
async def creset(ctx):
    devlogs = client.get_channel(settings.config["channels"]["devlog"])
    log = f"{utils.timestr}`cogs` loaded manually using !creset command"
    client.load_extension("cogs.developer")
    await utils.emoji(ctx)
    await devlogs.send(log)


client.run(sys.argv[3])
