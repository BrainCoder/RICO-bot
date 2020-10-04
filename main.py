from utils import *
from streak import *
#from moderation import *
client=commands.Bot(command_prefix='!')
#import moderation
import discord
import os
from discord.ext import commands
from discord.utils import get
import asyncio

#client.add_command(reset)
client.add_command(relapse)
client.add_command(update)
#client.add_listener(on_member_ban)
#client.add_command(clear)
#client.add_command(kick)
#client.add_command(ban)
#client.add_command(lynch)





#channels = {'botlog': 743056752446275596,
#            'botlab': 744145383592296588,
#            'streak': 745452658545918042}!update

async def mCount_update():
    threading.Timer(1800, mCount_update).start()
    for guild in client.guilds:
        if guild.id != 757696811497422969:
            continue
        mCount = guild.member_count
        channel = client.get_channel(761862028885229568)
        break
    print(f'There are now {mCount} mebers of this server')
    await channel.edit(name=(f'{mCount} members'))


@client.event
async def on_ready():
    print('Bot is active')
    await mCount_update()
    await client.change_presence(status=discord.Status.online, activity=discord.Game('DM me with complaints!'))



@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')



"""
async def monthStart():
    while True:
        now = datetime.today()
        y = now.year if now.month < 12 else now.year+1
        m = (now.month+1) if now.month < 12 else 1
        secondsToSleep = (datetime(y, m, 1) - datetime.today()).total_seconds()
        channel = client.get_channel(582650072672632833)
        await asyncio.sleep(secondsToSleep)
<<<<<<< HEAD
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

@client.event
async def on_ready():
    print('Bot is active')
    await mCount_update()
    await client.change_presence(status=discord.Status.online, activity=discord.Game('dm to speak with mods'))
    #asyncio.create_task(monthStart())
    #asyncio.create_task(hourly())

#async def hourly():
#    while True:
#        await asyncio.sleep(60*60)
#        for key in banDict:
#            if banDict[key] > 0:
#                banDict[key] -= 1
#            else:
#                del banDict[key]

@client.event
async def on_member_join(member):
    channel = client.get_channel(519455122602983424)
    await channel.send(f'{member.mention} welcome! Please go to <#519455164894019584> to read an overview of what this server is about. Go to <#519627611836776490> and <#567283111273037834> to see the commands that you can use to assign yourself.')

    #asyncio.create_task(monthStart())
    #asyncio.create_task(hourly())


# To ignore command not found and command check exceptions:
# Use the error cog given in the discord.api support server
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound) or isinstance(error, CheckFailure):
        return
    raise error







## DM Cog

@client.event
async def on_message(message):
    channel = client.get_channel(699110029806272592)
    if message.guild is None and message.author != client.user:
        await channel.send(f"<@{message.author.id}> said: {message.content}")
    await client.process_commands(message)

@client.command(checks=[is_in_channel2()])
async def dm(ctx, member: discord.Member, *, content):
    channel = await member.create_dm()
    await channel.send(content)

## /DM Cog

## Checklist function

@client.command(checks=[is_in_channel3()])
async def cl(ctx,*,message):
    channel = client.get_channel(758576163630350366)
    await channel.send(f"<@{ctx.author.id}>: \n{message}")


@client.command()
@commands.has_permissions(administrator=True)
async def logout(ctx):
  await ctx.message.delete()
  await ctx.send("logging out")
  await ctx.send("logged out")
  exit()



client.run('NzYwNTkzODQwNDE5MjQyMDI0.X3OUNg.LUpzU6B589BBRfca5ae1BnS1wv4')

#with open ('token.txt', 'rt') as myfile:
 #       contents = myfile.read()
  #      client.run(f'{contents}')
