from utils import *
from streak import *
#from moderation import *
client=commands.Bot(command_prefix='!')
import moderation
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

@client.event
async def on_ready():
    print('Bot is active')
    await client.change_presence(status=discord.Status.online, activity=discord.Game('dm to speak with mods'))
    #asyncio.create_task(monthStart())
    #asyncio.create_task(hourly())


# To ignore command not found and command check exceptions:
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound) or isinstance(error, CheckFailure):
        return
    raise error


@client.event
async def on_message(message):
    channel = client.get_channel(758576163630350366)
    if message.guild is None and message.author != client.user:
        await channel.send(f"<@{message.author.id}> said: {message.content}")  # send messsage into channel
    await client.process_commands(message)

@client.command()
async def dm(ctx, member: discord.Member, *, content):
    channel = await member.create_dm()  # creates a DM channel for mentioned user
    await channel.send(content)  # send whatever in the content to the mentioned user.



@client.command()
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def nuke(ctx, amount=100000):
      await ctx.message.delete()
      await ctx.channel.purge(limit=amount)
      await ctx.send("chat nuked")

#@commands.is_owner()  # The account that owns the bot





@client.command()
@commands.has_permissions(administrator=True)
async def avatar(ctx, *,  avamember : discord.Member=None):
    userAvatarUrl = avamember.avatar_url
    await ctx.send(f"{ctx.author}'s avatar is: {userAvatarUrl}")

url2 = "https://emergency.nofap.com/director.php?cat=em&religious=false"



client.reaction_roles = []






@client.command()
async def dm_all(ctx, *, args=None):
    if args != None:
        members = ctx.guild.members
        for member in members:
            try:
                await member.send(args)
                print("'" + args + "' sent to: " + member.name)

            except:
                print("Couldn't send '" + args + "' to: " + member.name)

    else:
        await ctx.channel.send("A message was not provided.")


# uniqueCategoryNames = ['genderRoles', 'continentRoles', 'religionRoles', 'modeRoles']
# additionalCategoryName = 'otherRoles'
# categoryDictsList = list(map(lambda a: idData[a], uniqueCategoryNames+[additionalCategoryName]))
# combinedDict = functools.reduce(lambda a,b: {**a, **b}, categoryDictsList)
#
# uniqueRolesCategorized = list(map(lambda a: list(idData[a].keys()), uniqueCategoryNames))
# additionalRolesCategorized = list(idData[additionalCategoryName].keys())
# rolesLower = list(map(lambda a: a.lower(),combinedDict.keys()))
# @client.command(aliases=rolesLower)
# async def roleDistributor(ctx):
#     if(ctx.invoked_with == "roleDistributor"):
#         return
#     print(ctx.invoked_with)
#     ownedRoleIds = list(map(lambda a: a.id, ctx.author.roles))
#     formated = uniqueRolesCategorized+list(map(lambda a: [a], additionalRolesCategorized))
#     for category in formated:
#         if ctx.invoked_with in category:
#             for role in category:
#                 if combinedDict[role] in ownedRoleIds:
#                     if role in idData['genderRoles'].keys():
#                         return
#                     roleObj = ctx.guild.get_role(combinedDict[role])
#                     await member.remove_roles(roleObj)
#                     if role != ctx.invoked_with:
#                         roleObj = ctx.guild.get_role(combinedDict[ctx.invoked_with])
#                         await member.add_roles(roleObj)
#                     return
#             roleObj = ctx.guild.get_role(combinedDict[ctx.invoked_with])
#             await member.add_roles(roleObj)
#             return


client.run('NzYwNTkzODQwNDE5MjQyMDI0.X3OUNg.LUpzU6B589BBRfca5ae1BnS1wv4')

#NzQ5ODM2MjYzOTU1MTAzNzc0.X0xxcA.wrZ-tylfYU5k721t7kk3OI4LVRE No Porn

#NzYwNTc4OTIxNjMyMzY2NjQy.X3OGUQ.1dg11jaoJze7l6MVAAsccC0jXrQ Dank Meme

