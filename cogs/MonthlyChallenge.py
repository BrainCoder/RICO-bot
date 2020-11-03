import discord
from discord.ext import commands
import settings
intents = discord.Intents.all()
intents.members = True 
client=commands.Bot(command_prefix='!', intients=intents)

class MonthlyChallenge(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    #Events
    #@commands.Cog.listener()

    @commands.command(name="startchallenge", pass_context=True)
    @commands.has_any_role(
        settings.config["statusRoles"]["developer"])
    async def startChallenge(self, ctx):
        """starts that months monthly challenge"""
        newParticipants = []
        print('Starting new month now.')
        for discord.guild in self.client.guilds:
            signupRole = discord.guild.get_role(settings.config["otherRoles"]["monthly-challenge"])  # M-Challenge-Signup
            participationRole = discord.guild.get_role(settings.config["statusRoles"]["monthly-challenge-participant"])  # monthly-challenge-participant
            members = await discord.guild.fetch_members(limit=None).flatten()
            for member in members:
                for role in member.roles:
                    if role.id == settings.config["otherRoles"]["monthly-challenge"]:  # M-Challenge-Signup
                        self.client.loop.create_task(member.remove_roles(signupRole))
                        newParticipants.append(member)
                        self.client.loop.create_task(member.add_roles(participationRole))
                        break
        await ctx.send(f"Challenge participants {len(newParticipants)}")
        print(len(newParticipants))

    @commands.command(name="endchallenge", pass_context=True)
    @commands.has_any_role(
        settings.config["statusRoles"]["developer"])
    async def endChallenge(self, ctx):
        """ends that monthly challenge"""
        newParticipants = []
        print('Ending challenge now.')
        for discord.guild in self.client.guilds:
            participationrole = discord.guild.get_role(settings.config["statusRoles"]["monthly-challenge-participant"])  # monthly-challenge-participant
            winnerrole = discord.guild.get_role(settings.config["statusRoles"]["monthly-challenge-winner"])  # Challenge Winner
            nnn2020 = discord.guild.get_role(settings.config["statusRoles"]["nnn2020"])  # Challenge Winner
            members = await discord.guild.fetch_members(limit=None).flatten()
            for member in members:
                for role in member.roles:
                    if role.id == settings.config["statusRoles"]["monthly-challenge-participant"]:  # monthly-challenge-participant
                        self.client.loop.create_task(member.remove_roles(participationrole))
                        newParticipants.append(member)
                        self.client.loop.create_task(member.add_roles(winnerrole))
                        self.client.loop.create_task(member.add_roles(nnn2020))
                        break
        await ctx.send(f"Challenge Winners {len(newParticipants)}")
        print(len(newParticipants))


    @commands.command(name="participation", pass_context=True)
    async def participation_amount(self, ctx):
        """sends the current number of users with the M-Challenge participant role"""
        guild = ctx.guild
        role = guild.get_role(settings.config["statusRoles"]["monthly-challenge-participant"]) # monthly-challenge-participant
        partcipants = [m for m in guild.members if role in m.roles]
        no = len(partcipants)
        print(f'{no}')
        await ctx.send(f'Monthly Challenge members left: {no}')

def setup(client):
    client.add_cog(MonthlyChallenge(client))
