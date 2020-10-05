from utils import *
from streak import *

client=commands.Bot(command_prefix='!')
import discord
import os
from discord.ext import commands
from discord.utils import get
import asyncio

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

#Member count plus game status
async def mCount_update():
    threading.Timer(1800, mCount_update).start()
    for guild in client.guilds:
        if guild.id != 519330541720436736:
            continue
        mCount = guild.member_count
        channel = client.get_channel(761264831981682718)
        break
    print(f'There are now {mCount} mebers of this server')
    await channel.edit(name=(f'{mCount} members'))




"""@client.command(pass_context=True)
@commands.has_permissions(ban_members=True)
async def endChallenge(ctx):
    newParticipants = []
    print('Ending challenge now.')
    for discord.guild in client.guilds:
        signupRole = discord.guild.get_role(761079978749067274)  # MonthlyChallenge-participant
        participationRole = discord.guild.get_role(761073836455362560)  # Challenge Winner
        members = await discord.guild.fetch_members(limit=None).flatten()
        newParticipants = []
        for member in members:
            for role in member.roles:
                if role.id == 761079978749067274:  # MonthlyChallenge-participant
                    client.loop.create_task(member.remove_roles(signupRole))
                    client.loop.create_task(member.remove_roles(signupRole))
                    newParticipants.append(member)
                    client.loop.create_task(member.add_roles(participationRole))
                    break
    await ctx.send(f"Challenge Winners {len(newParticipants)}")
    print(len(newParticipants))"""


@client.event
async def on_ready():
    print('Bot is active')
    await mCount_update()
    await client.change_presence(status=discord.Status.online, activity=discord.Game('DM me with complaints!'))
#/Member count plus game status





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


@client.event
async def on_member_join(member):
    channel = client.get_channel(519455122602983424)
    await channel.send(f'{member.mention} welcome! Please go to <#519455164894019584> to read an overview of what this server is about. Go to <#519627611836776490> and <#567283111273037834> to see the commands that you can use to assign yourself.')
#/Cogs

#    asyncio.create_task(monthStart())
  #  asyncio.create_task(hourly())


# To ignore command not found and command check exceptions:
# Use the error cog given in the discord.api support server
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound) or isinstance(error, CheckFailure):
        return
    raise error







## DM Cog


#Complaints DM code
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
#/Complaints DM code

## /DM Cog

## Checklist function





#with open ('token.txt', 'rt') as myfile:
 #       contents = myfile.read()
  #      client.run(f'{contents}')
#Self destruct
@client.command()
@commands.has_permissions(administrator=True)
async def logout(ctx):
  await ctx.message.delete()
  await ctx.send("logging out")
  exit()
#Self destruct




#client.run('NzQ5ODM2MjYzOTU1MTAzNzc0.X0xxcA.GYgm0dLg7RX8-8sMUvOTsZtGakc')

with open ('token.txt', 'rt') as myfile:
    contents = myfile.read()
    client.run(f'{contents}')
