import discord
from discord.ext import commands
import settings
import utils

class MonthlyChallenge(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @commands.command(name="participation", pass_context=True)
    async def participation_amount(self, ctx):
        """sends the current number of users with the M-Challenge participant role"""
        mrole = ctx.guild.get_role(settings.config["statusRoles"]["monthly-challenge-participant"])
        yrole = ctx.guild.get_role(settings.config["statusRoles"]["yearly-challenge-participant"])
        mpartcipants = [m for m in ctx.guild.members if mrole in m.roles]
        ypartcipants = [m for m in ctx.guild.members if yrole in m.roles]
        mno = len(mpartcipants)
        yno = len(ypartcipants)
        print(f'{mno}')
        print(f'{yno}')
        await utils.doembed(ctx, "Challenge statics", "Participation", f"\nMonthly Challenge Memebers left: {mno}\n Yearly Challenge Members left: {yno}", ctx.author, True)

    # Monthly Challenge

    @commands.command(name="mstartchallenge", pass_context=True)
    @commands.has_any_role(
        settings.config["statusRoles"]["developer"])
    async def mstartChallenge(self, ctx):
        """starts that months monthly challenge"""
        newParticipants = []
        print('Starting new month now.')
        for discord.guild in self.client.guilds:
            signupRole = discord.guild.get_role(settings.config["otherRoles"]["monthly-challenge"])
            participationRole = discord.guild.get_role(settings.config["statusRoles"]["monthly-challenge-participant"])
            members = await discord.guild.fetch_members(limit=None).flatten()
            for member in members:
                for role in member.roles:
                    if role.id == settings.config["otherRoles"]["monthly-challenge"]:
                        self.client.loop.create_task(member.remove_roles(signupRole))
                        newParticipants.append(member)
                        self.client.loop.create_task(member.add_roles(participationRole))
                        break
        await ctx.send(f"Challenge participants {len(newParticipants)}")
        print(len(newParticipants))

    @commands.command(name="mendchallenge", pass_context=True)
    @commands.has_any_role(
        settings.config["statusRoles"]["developer"])
    async def mendChallenge(self, ctx):
        """ends that monthly challenge"""
        newParticipants = []
        print('Ending challenge now.')
        for discord.guild in self.client.guilds:
            participationrole = discord.guild.get_role(settings.config["statusRoles"]["monthly-challenge-participant"])
            winnerrole = discord.guild.get_role(settings.config["statusRoles"]["monthly-challenge-winner"])
            members = await discord.guild.fetch_members(limit=None).flatten()
            for member in members:
                for role in member.roles:
                    if role.id == settings.config["statusRoles"]["monthly-challenge-participant"]:
                        self.client.loop.create_task(member.remove_roles(participationrole))
                        newParticipants.append(member)
                        self.client.loop.create_task(member.add_roles(winnerrole))
                        break
        await ctx.send(f"Challenge Winners {len(newParticipants)}")
        print(len(newParticipants))

    # Yearly challenge

    @commands.command(name="yearlychallenge")
    async def yearlychallenge(self, ctx):
        """gives the user the yearly challenge role"""
        signup_role = ctx.guild.get_role(settings.config["otherRoles"]["yearly-challenge"])
        await ctx.author.add_roles(signup_role)
        await utils.emoji(ctx, '✅')

    @commands.command(name="ystartchallenge", pass_context=True)
    @commands.has_any_role(
        settings.config["statusRoles"]["developer"])
    async def ystartChallenge(self, ctx):
        """starts that months monthly challenge"""
        newParticipants = []
        print('Starting new month now.')
        for discord.guild in self.client.guilds:
            signupRole = discord.guild.get_role(settings.config["otherRoles"]["yearly-challenge"])
            participationRole = discord.guild.get_role(settings.config["statusRoles"]["yearly-challenge-participant"])
            members = await discord.guild.fetch_members(limit=None).flatten()
            for member in members:
                for role in member.roles:
                    if role.id == settings.config["otherRoles"]["yearly-challenge"]:
                        self.client.loop.create_task(member.remove_roles(signupRole))
                        newParticipants.append(member)
                        self.client.loop.create_task(member.add_roles(participationRole))
                        break
        await ctx.send(f"Challenge participants {len(newParticipants)}")
        print(len(newParticipants))

    @commands.command(name="yendchallenge", pass_context=True)
    @commands.has_any_role(
        settings.config["statusRoles"]["developer"])
    async def yendChallenge(self, ctx):
        """ends that monthly challenge"""
        newParticipants = []
        print('Ending challenge now.')
        for discord.guild in self.client.guilds:
            participationrole = discord.guild.get_role(settings.config["statusRoles"]["yearly-challenge-participant"])
            winnerrole = discord.guild.get_role(settings.config["statusRoles"]["2021-challenge-winner"])
            members = await discord.guild.fetch_members(limit=None).flatten()
            for member in members:
                for role in member.roles:
                    if role.id == settings.config["statusRoles"]["yearly-challenge-participant"]:
                        self.client.loop.create_task(member.remove_roles(participationrole))
                        newParticipants.append(member)
                        self.client.loop.create_task(member.add_roles(winnerrole))
                        break
        await ctx.send(f"Challenge Winners {len(newParticipants)}")
        print(len(newParticipants))


def setup(client):
    client.add_cog(MonthlyChallenge(client))
