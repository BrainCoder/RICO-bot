import discord
from discord.ext import commands
import settings
import utils

async def challengeStart(self, ctx, signupRole, participationRole):
    newParticipants = []
    print('Starting new month now.')
    for discord.guild in client.guilds:
        signupR = discord.guild.get_role(signupRole)
        participationR = discord.guild.get_role(participationRole)
        members = await discord.guild.fetch_members(limit=None).flatten()
        for member in members:
            for role in member.roles:
                if role.id == signupRole:
                    client.loop.create_task(member.remove_roles(signupR))
                    newParticipants.append(member)
                    client.loop.create_task(member.add_roles(participationR))
                    break
    await ctx.send(f"Challenge participants {len(newParticipants)}")
    print(len(newParticipants))

async def challengeEnd(self, ctx, participationRole, winnerRole):
    newParticipants = []
    print('Starting new month now.')
    for discord.guild in client.guilds:
        signupR = discord.guild.get_role(participationRole)
        participationR = discord.guild.get_role(winnerRole)
        members = await discord.guild.fetch_members(limit=None).flatten()
        for member in members:
            for role in member.roles:
                if role.id == participationRole:
                    client.loop.create_task(member.remove_roles(signupR))
                    newParticipants.append(member)
                    client.loop.create_task(member.add_roles(participationR))
                    break
    await ctx.send(f"Challenge participants {len(newParticipants)}")
    print(len(newParticipants))

class MonthlyChallenge(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @commands.command(name="participation", pass_context=True)
    async def participation_amount(self, ctx):
        """sends the current number of users with the M-Challenge participant role"""
        mpartcipants = [m for m in ctx.guild.members if ctx.guild.get_role(settings.config["challenges"]["monthlyChallengeParticipant"]) in m.roles]
        ypartcipants = [m for m in ctx.guild.members if ctx.guild.get_role(settings.config["challenges"]["yearlyChallengeParticipant"]) in m.roles]
        dparticipants = [m for m in ctx.guild.members if ctx.guild.get_role(settings.config["challenges"]["deadpoolParticipant"]) in m.roles]
        mno = len(mpartcipants)
        yno = len(ypartcipants)
        dno = len(dparticipants)
        await utils.doembed(ctx, "Challenge statics", "Participation", f"\nMonthly Challenge Memebers left: {mno}\nYearly Challenge Members left: {yno}\nDeadpool Challenge Members Left: {dno}", ctx.author, True)

    # Monthly Challenge

    @commands.command(name='monthly')
    @commands.has_any_role(
        settings.config["staffRoles"]["developer"])
    async def monthly(self, ctx, action=None):
        if action is None:
            await ctx.send('Please specify the apropriate arguments for this command')
        if action == 'start':
            await utils.emoji(ctx, '✅')
            await challengeStart(ctx, settings.config["challenges"]["monthlyChallengeSignup"], settings.config["challenges"]["monthlyChallengeParticipant"])
        if action == 'ends':
            await utils.emoji(ctx, '✅')
            await challengeEnd(ctx, settings.config["challenges"]["monthlyChallengeParticipant"], settings.config["challenges"]["monthlyChallengeWinner"])

    # Yearly challenge

    @commands.command(name="yearlychallenge")
    async def yearlychallenge(self, ctx):
        """gives the user the yearly challenge role"""
        signup_role = ctx.guild.get_role(settings.config["challenges"]["yearlyChallengeSignup"])
        await ctx.author.add_roles(signup_role)
        await utils.emoji(ctx, '✅')

    @commands.command(name='yearly')
    @commands.has_any_role(
        settings.config["staffRoles"]["developer"])
    async def yearly(self, ctx, action=None):
        """Command used to manage the deapool challenge\nStart - Gives everyone w/ the signup role the participant role\nEnd - Gives the finial memeber the winner role"""
        if action is None:
            await ctx.send('Please specify the apropriate arguments for this command')
        if action == 'start':
            await utils.emoji(ctx, '✅')
            await challengeStart(ctx, settings.config["challenges"]["yearlyChallengeSignup"], settings.config["challenges"]["yearlyChallengeParticipant"])
        if action == 'ends':
            await utils.emoji(ctx, '✅')
            await challengeEnd(ctx, settings.config["challenges"]["yearlyChallengeParticipant"], settings.config["challenges"]["2021ChallengeWinner"])

    @commands.command(name='deadpool')
    @commands.has_any_role(
        settings.config["staffRoles"]["developer"])
    async def deadpool(self, ctx, action=None):
        """Command used to manage the deapool challenge\nStart - Gives everyone w/ the signup role the participant role\nEnd - Gives the finial memeber the winner role"""
        if action is None:
            await ctx.send('Please specify the apropriate arguments for this command')
        if action == 'start':
            await utils.emoji(ctx, '✅')
            await challengeStart(ctx, settings.config["challenges"]["deadpoolSignup"], settings.config["challenges"]["deadpoolParticipant"])
        if action == 'ends':
            await utils.emoji(ctx, '✅')
            await challengeEnd(ctx, settings.config["challenges"]["deadpoolParticipant"], settings.config["challenges"]["deadpoolWinner"])


def setup(client):
    client.add_cog(MonthlyChallenge(client))
