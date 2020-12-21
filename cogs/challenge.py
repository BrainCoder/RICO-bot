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
        mrole = ctx.guild.get_role(settings.config["challenges"]["monthlyChallengeParticipant"])
        yrole = ctx.guild.get_role(settings.config["challenges"]["yearlyChallengeParticipant"])
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
        settings.config["staffRoles"]["developer"])
    async def mstartChallenge(self, ctx):
        """starts that months monthly challenge"""
        await utils.emoji(ctx, '✅')
        newParticipants = []
        print('Starting new month now.')
        for discord.guild in self.client.guilds:
            signupRole = discord.guild.get_role(settings.config["challenges"]["monthlyChallengeSignup"])
            participationRole = discord.guild.get_role(settings.config["challenges"]["monthlyChallengeParticipant"])
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
        settings.config["staffRoles"]["developer"])
    async def mendChallenge(self, ctx):
        """ends that monthly challenge"""
        await utils.emoji(ctx, '✅')
        newParticipants = []
        print('Ending challenge now.')
        for discord.guild in self.client.guilds:
            participationrole = discord.guild.get_role(settings.config["challenges"]["monthlyChallengeParticipant"])
            winnerrole = discord.guild.get_role(settings.config["challenges"]["monthlyChallengeWinner"])
            members = await discord.guild.fetch_members(limit=None).flatten()
            for member in members:
                for role in member.roles:
                    if role.id == settings.config["challenges"]["monthlyChallengeParticipant"]:
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
        signup_role = ctx.guild.get_role(settings.config["challenges"]["yearlyChallengeSignup"])
        await ctx.author.add_roles(signup_role)
        await utils.emoji(ctx, '✅')

    @commands.command(name="ystartchallenge", pass_context=True)
    @commands.has_any_role(
        settings.config["staffRoles"]["developer"])
    async def ystartChallenge(self, ctx):
        """starts that months monthly challenge"""
        await utils.emoji(ctx, '✅')
        newParticipants = []
        print('Starting new month now.')
        for discord.guild in self.client.guilds:
            signupRole = discord.guild.get_role(settings.config["challenges"]["yearlyChallengeSignup"])
            participationRole = discord.guild.get_role(settings.config["challenges"]["yearlyChallengeParticipant"])
            members = await discord.guild.fetch_members(limit=None).flatten()
            for member in members:
                for role in member.roles:
                    if role.id == settings.config["challenges"]["yearlyChallengeSignup"]:
                        self.client.loop.create_task(member.remove_roles(signupRole))
                        newParticipants.append(member)
                        self.client.loop.create_task(member.add_roles(participationRole))
                        break
        await ctx.send(f"Challenge participants {len(newParticipants)}")
        print(len(newParticipants))

    @commands.command(name="yendchallenge", pass_context=True)
    @commands.has_any_role(
        settings.config["staffRoles"]["developer"])
    async def yendChallenge(self, ctx):
        """ends that monthly challenge"""
        await utils.emoji(ctx, '✅')
        newParticipants = []
        print('Ending challenge now.')
        for discord.guild in self.client.guilds:
            participationrole = discord.guild.get_role(settings.config["challenges"]["monthlyChallengeParticipant"])
            winnerrole = discord.guild.get_role(settings.config["challenges"]["2021-challenge-winner"])
            members = await discord.guild.fetch_members(limit=None).flatten()
            for member in members:
                for role in member.roles:
                    if role.id == settings.config["challenges"]["monthlyChallengeParticipant"]:
                        self.client.loop.create_task(member.remove_roles(participationrole))
                        newParticipants.append(member)
                        self.client.loop.create_task(member.add_roles(winnerrole))
                        break
        await ctx.send(f"Challenge Winners {len(newParticipants)}")
        print(len(newParticipants))


def setup(client):
    client.add_cog(MonthlyChallenge(client))
