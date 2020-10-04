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

@client.event
async def on_ready():
    print('Bot is active')
    await mCount_update()
    await client.change_presence(status=discord.Status.online, activity=discord.Game('DM me with complaints!'))

@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'loaded {extension}')

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'unloaded {extension}')

@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'reloaded {extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

@client.event
async def on_member_join(member):
    channel = client.get_channel(519455122602983424)#welcome
    await channel.send(f'{member.mention} welcome! Please go to <#519455164894019584> to read an overview of what this server is about. Go to <#519627611836776490> and <#567283111273037834> to see the commands that you can use to assign yourself.')

## DM Cog

@client.event
async def on_message(message):
    channel = client.get_channel(699110029806272592)#complaints
    if message.guild is None and message.author != client.user:
        await channel.send(f"<@{message.author.id}> said: {message.content}")
    await client.process_commands(message)

@client.command(checks=[is_in_channel2()])
async def dm(ctx, member: discord.Member, *, content):
    channel = await member.create_dm()
    await channel.send(content)

## /DM Cog

@client.command()
@commands.has_permissions(administrator=True)
async def logout(ctx):
  await ctx.message.delete()
  await ctx.send("logging out")
  await ctx.send("logged out")
  exit()

#client.run('NzYwNTkzODQwNDE5MjQyMDI0.X3OUNg.LUpzU6B589BBRfca5ae1BnS1wv4')

with open ('token.txt', 'rt') as myfile:
    contents = myfile.read()
    client.run(f'{contents}')
