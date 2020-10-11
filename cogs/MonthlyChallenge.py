import discord
from discord.ext import commands
from discord.utils import get

intents = discord.Intents.all()
intents.members = True 

class MonthlyChallenge(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    #Events
    #@commands.Cog.listener()

    @commands.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def startChallenge(self, ctx):
        newParticipants = []
        print('Starting new month now.')
        for discord.guild in self.client.guilds:
            signupRole = discord.guild.get_role(582648694017490945)  # M-Challenge-Signup
            participationRole = discord.guild.get_role(582640858378272793)  # MonthlyChallenge-participant
            members = await discord.guild.fetch_members(limit=None).flatten()
            for member in members:
                for role in member.roles:
                    if role.id == 760702609207590962:  # M-Challenge-Signup
                        self.client.loop.create_task(member.remove_roles(signupRole))
                        newParticipants.append(member)
                        self.client.loop.create_task(member.add_roles(participationRole))
                        break
        await ctx.send(f"Challenge participants {len(newParticipants)}")
        print(len(newParticipants))

    @commands.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def endChallenge(self, ctx):
        newParticipants = []
        print('Ending challenge now.')
        for discord.guild in self.client.guilds:
            signupRole = discord.guild.get_role(582640858378272793)  # MonthlyChallenge-participant
            participationRole = discord.guild.get_role(582649176601657365)  # Challenge Winner
            members = await discord.guild.fetch_members(limit=None).flatten()
            for member in members:
                for role in member.roles:
                    if role.id == 761079978749067274:  # MonthlyChallenge-participant
                        self.client.loop.create_task(member.remove_roles(signupRole))
                        newParticipants.append(member)
                        self.client.loop.create_task(member.add_roles(participationRole))
                        break
        await ctx.send(f"Challenge Winners {len(newParticipants)}")
        print(len(newParticipants))


    @commands.command(pass_context=True)
    @commands.has_any_role('M-Challenge_Participant', 'owners')
    async def participation_amount(self, ctx):
        newParticipants = []
        for discord.guild in self.client.guilds:
            signupRole = discord.guild.get_role(582640858378272793)  # MonthlyChallenge-participant
            members = await discord.guild.fetch_members(limit=None).flatten()
            for member in members:
                for role in member.roles:
                    if role.id == 582640858378272793:  # MonthlyChallenge-participant
                        if (newParticipants.append(member) != None):
                            newParticipants.append(member)
                            break
        await ctx.send(f"Monthly Challenge Members Left: {len(newParticipants)}")
        print(len(newParticipants))

    @commands.command()
    @commands.has_any_role('Developer')
    async def participation_amount2(self, ctx):
        guild = ctx.guild
        role = guild.get_role(582640858378272793)
        partcipants = [m for m in guild.members if role in m.roles]
        no = len(partcipants)
        print(f'{no}')
        await ctx.send(f'Monthly Challenge members left: {no}')
        
    @commands.command(pass_context=True)
    async def signup_amount(self, ctx):
        newSignups = []
        for discord.guild in self.client.guilds:
            signupRole = discord.guild.get_role(582648694017490945)  # MonthlyChallenge-signup
            members = await discord.guild.fetch_members(limit=None).flatten()
            for member in members:
                for role in member.roles:
                    if role.id == 582648694017490945:  # MonthlyChallenge-signup
                        if (newSignups.append(member) != None):
                            newSignups.append(member)
                            break
        await ctx.send(f"Monthly Challenge Members Left: {len(newSignups)}")
        print(len(newSignups))

    @commands.command(pass_context=True)
    async def winner_amount(self, ctx):
        newWinners = []
        for discord.guild in self.client.guilds:
            signupRole = discord.guild.get_role(582648694017490945)  # MonthlyChallenge-signup
            members = await discord.guild.fetch_members(limit=None).flatten()
            for member in members:
                for role in member.roles:
                    if role.id == 582648694017490945:  # MonthlyChallenge-signup
                        if (newWinners.append(member) != None):
                            newWinners.append(member)
                            break
        await ctx.send(f"Monthly Challenge Members Left: {len(newWinners)}")
        print(len(newWinners))

def setup(client):
    client.add_cog(MonthlyChallenge(client))
