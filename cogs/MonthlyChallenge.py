import discord
from discord.ext import commands
from discord.utils import get

client=commands.Bot(command_prefix='!')
class MonthlyChallenge(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    #Events
    #@commands.Cog.listener()

    @commands.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def endChallenge(self, ctx):
        print('Ending challenge now.')
        for discord.guild in self.client.guilds:
            signupRole = discord.guild.get_role(582640858378272793)  # MonthlyChallenge-participant
            participationRole = discord.guild.get_role(582649176601657365)  # Challenge Winner
            members = await discord.guild.fetch_members(limit=None).flatten()
            newParticipants = []
            for member in members:
                for role in member.roles:
                    if role.id == 582640858378272793:  # MonthlyChallenge-participant
                        client.loop.create_task(member.remove_roles(signupRole))
                        newParticipants.append(member)
                        client.loop.create_task(member.add_roles(participationRole))
                        break
            await ctx.send(f"Challenge Winners {len(newParticipants)}")
            print(len(newParticipants))

    @commands.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def startChallenge(self, ctx):
        print('Starting new month now.')
        for discord.guild in self.client.guilds:
            print ('hello')
            signupRole = discord.guild.get_role(582648694017490945)  # M-Challenge-Signup
            participationRole = discord.guild.get_role(582640858378272793)  # MonthlyChallenge-participant
            members = await discord.guild.fetch_members(limit=None).flatten()
            newParticipants = []
            for member in members:
                for role in member.roles:
                    if role.id == 582648694017490945:  # M-Challenge-Signup
                        client.loop.create_task(member.remove_roles(signupRole))
                        newParticipants.append(member)
                        client.loop.create_task(member.add_roles(participationRole))
                        break

            await ctx.send(f"Challenge participants {len(newParticipants)}")
            print(len(newParticipants))



def setup(client):
    client.add_cog(MonthlyChallenge(client))
