from discord.ext import commands
import settings
import utils
import sys
import traceback
from datetime import datetime, timedelta

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
        await chalToggle(ctx, settings.config["challenges"]["monthly-challenge-signup"], settings.config["challenges"]["monthly-challenge-participant"])
        await channel.send(f'<@{settings.config["challenges"]["monthly-challenge-participant"]}> the new monthly challenge has started! Please be sure to grab the role again to be signed up for the next one')
    if action == 'stop':
        await chalToggle(ctx, settings.config["challenges"]["monthly-challenge-participant"], settings.config["challenges"]["monthly-challenge-winner"])

async def yearly(ctx, action):
    if action == 'start':
        await chalToggle(ctx, settings.config["challenges"]["yearly-challenge-signup"], settings.config["challenges"]["yearly-challenge-participant"])
    if action == 'stop':
        await chalToggle(ctx, settings.config["challenges"]["yearly-challenge-participant"], settings.config["challenges"]["2021-challenge-winner"])

async def deadpool(ctx, action):
    if action == 'start':
        await chalToggle(ctx, settings.config["challenges"]["deadpool-signup"], settings.config["challenges"]["deadpool-participant"])
    if action == 'stop':
        await chalToggle(ctx, settings.config["challenges"]["deadpool-participant"], settings.config["challenges"]["deadpool-winner"])

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
            await ctx.send('Please selected the challenge and/or action you would like to commit')
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command(name="participation", pass_context=True)
    async def participation_amount(self, ctx):
        """sends the current number of users with the M-Challenge participant role"""
        mpartcipants = len(await utils.rolePop(ctx, settings.config["challenges"]["monthly-challenge-participant"]))
        ypartcipants = len(await utils.rolePop(ctx, settings.config["challenges"]["yearly-challenge-participant"]))
        dparticipants = len(await utils.rolePop(settings.config["challenges"]["deadpool-participant"]))
        await utils.doembed(ctx, "Challenge statics", "Participation", f"\nMonthly Challenge Memebers left: {mpartcipants}\nYearly Challenge Members left: {ypartcipants}\nDeadpool Challenge Members Left: {dparticipants}", ctx.author, True)

    @commands.command(name="yearlychallenge")
    async def yearlychallenge(self, ctx):
        """gives the user the yearly challenge role"""
        signup_role = ctx.guild.get_role(settings.config["challenges"]["yearly-challenge-signup"])
        await ctx.author.add_roles(signup_role)
        await utils.emoji(ctx, '✅')

    @commands.command(name='deadpool')
    async def deadpoolSingup(self, ctx):
        user_query = utils.userdata.select().where(utils.userdata.c.id == ctx.author.id)
        result = utils.conn.execute(user_query).fetchone()
        if result[1] is not None and result[1] != 0:
            past_streak_time = datetime.fromtimestamp(result[1])
            if datetime.now() > past_streak_time + timedelta(days=30):
                await ctx.channel.send("Cannot join because you're too far along in your streak. Congratulations!")
                return
        else:
            await ctx.channel.send("No streak data found. Please set your streak before entering the competition.")
            return
        signupRole = ctx.guild.get_role(settings.config["challenges"]["deadpool-signup"])
        await ctx.author.add_roles(signupRole)
        await utils.emoji(ctx, '✅')

def setup(client):
    client.add_cog(MonthlyChallenge(client))
