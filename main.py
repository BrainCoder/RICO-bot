from utils import *
from streak import *
from moderation import *
client=commands.Bot(command_prefix='!')
#client.add_command(reset)
client.add_command(relapse)
client.add_command(update)
client.add_listener(on_member_ban)
#client.add_command(clear)
#client.add_command(kick)
#client.add_command(ban)
#client.add_command(lynch)



#channels = {'botlog': 743056752446275596,
#            'botlab': 744145383592296588,
#            'streak': 745452658545918042}!update



async def monthStart():
    while True:
        now = datetime.today()
        y = now.year if now.month < 12 else now.year+1
        m = (now.month+1) if now.month < 12 else 1
        secondsToSleep = (datetime(y, m, 1) - datetime.today()).total_seconds()
        await asyncio.sleep(secondsToSleep)
        await startChallenge()

async def hourly():
    while True:
        await asyncio.sleep(60*60)
        for key in banDict:
            if banDict[key] > 0:
                banDict[key] -= 1
            else:
                del banDict[key]

@client.event
async def on_ready():
    print('Bot is active')

    asyncio.create_task(monthStart())
    asyncio.create_task(hourly())


# To ignore command not found and command check exceptions:
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound) or isinstance(error, CheckFailure):
        return
    raise error

async def startChallenge():
    print('Starting new month now.')
    for guild in client.guilds:
        signupRole = guild.get_role(roles['teamchallenge-signup'])
        members = await guild.fetch_members(limit=None).flatten()
        newParticipants = []
        for member in members:
            for role in member.roles:
                if role.id == roles['teamchallenge-signup']:
                    client.loop.create_task(member.remove_roles(signupRole))
                    newParticipants.append(member)
                    break
        print(len(newParticipants))




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


client.run('NzQ5ODM2MjYzOTU1MTAzNzc0.X0xxcA.lMlc9yHnXkr_tJC9xVXtAefUGD0')
