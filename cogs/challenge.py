from discord.ext import commands
import settings
import utils
import sys
import traceback

async def chalToggle(ctx, beforeRole, afterRole):
    await utils.emoji(ctx, '✅')
    newParticipants = []
    print('Starting new month now.')
    before = ctx.guild.get_role(beforeRole)
    after = ctx.guild.get_role(afterRole)
    members = await ctx.guild.fetch_members(limit=None).flatten()
    for member in members:
        for role in member.roles:
            if role.id == beforeRole:
                await member.add_roles(after)
                newParticipants.append(member)
                await member.remove_roles(before)
                break
    await ctx.send(f"Challenge participants {len(newParticipants)}")
    print(len(newParticipants))

async def monthly(ctx, action):
    channel = ctx.guild.get_channel(settings.config["channels"]["monthly-challenge"])
    if action == 'start':
        await chalToggle(ctx, settings.config["challenges"]["monthlyChallengeSignup"], settings.config["challenges"]["monthlyChallengeParticipant"])
        await channel.send(f'<@{settings.config["challenges"]["monthlyChallengeParticipant"]}> the new monthly challenge has started! Please be sure to grab the role again to be signed up for the next one')
    if action == 'stop':
        await chalToggle(ctx, settings.config["challenges"]["monthlyChallengeParticipant"], settings.config["challenges"]["monthlyChallengeWinner"])

async def yearly(ctx, action):
    if action == 'start':
        await chalToggle(ctx, settings.config["challenges"]["yearlyChallengeSignup"], settings.config["challenges"]["yearlyChallengeParticipant"])
    if action == 'stop':
        await chalToggle(ctx, settings.config["challenges"]["yearlyChallengeParticipant"], settings.config["challenges"]["2021ChallengeWinner"])

async def deadpool(ctx, action):
    if action == 'start':
        await chalToggle(ctx, settings.config["challenges"]["deadpoolSignup"], settings.config["challenges"]["deadpoolParticipant"])
    if action == 'stop':
        await chalToggle(ctx, settings.config["challenges"]["deadpoolParticipant"], settings.config["challenges"]["deadpoolWinner"])

class MonthlyChallenge(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @commands.command(name='challenge', aliases=['chal'])
    @commands.has_any_role(
        settings.config["staffRoles"]["developer"])
    async def challenge(self, ctx, challenge, action):
        """Simmilar to the cog toggle, this allows the for easy starting and restarting of all chaellenges on the server"""
        if challenge == 'monthly':
            await monthly(ctx, action)
        if challenge == 'yearly':
            await yearly(ctx, action)
        if challenge == 'deadpool':
            await deadpool(ctx, action)
    @challenge.error
    async def challeneHandler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await utils.emoji(ctx, '❌')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please selected the challene and/or action you would like to commit')
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

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

    @commands.command(name="yearlychallenge")
    async def yearlychallenge(self, ctx):
        """gives the user the yearly challenge role"""
        signup_role = ctx.guild.get_role(settings.config["challenges"]["yearlyChallengeSignup"])
        await ctx.author.add_roles(signup_role)
        await utils.emoji(ctx, '✅')

    @commands.command(name='deadpool')
    async def deadpoolSingup(self, ctx):
        # I need a check here to make sure the users streak is under 30 days, gunna rely on squirrel for that
        signupRole = ctx.guild.get_role(settings.config["challenges"]["deadpoolSignup"])
        await ctx.author.add_roles(signupRole)
        await utils.emoji(ctx, '✅')

def setup(client):
    client.add_cog(MonthlyChallenge(client))
