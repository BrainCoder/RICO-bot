import utils
import database

from discord.ext import commands, tasks
import settings
import sys
import traceback
from datetime import datetime, timedelta
from sqlalchemy import text


class MonthlyChallenge(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None
        self.update_challenge_data.start()

    async def chal_toggle(self, ctx, beforeRole, afterRole):
        await utils.emoji(ctx)
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


    @commands.command(name='challenge', aliases=['chal'])
    @commands.has_any_role(
        settings.config["staffRoles"]["head-dev"],
        settings.config["staffRoles"]["developer"])
    async def challenge(self, ctx, challenge, action):
        """This is the command to manage the starting and stopping of all challenges running on the servers, as it
        stands the three challenges are 'Monthly Challenge', 'Yearly Challenge', 'Deadpool Challenge'.

        Args:
            **challenge:** This is the challenge you want to toggle, please enter 'monthly', 'yearly', or 'deadpool'
            **action:** This is where you specify wether you want to start or stop the challenge, please be aware that
             these actions can take large amount of time to complete. Do not spam the command, if you are concerned
              about how long it taking please contact a developer"
        """
        if challenge == 'monthly':
            channel = ctx.guild.get_channel(settings.config["channels"]["monthly-challenge"])
            role = ctx.guild.get_role(settings.config["challenges"]["monthly-challenge-participant"])
            if action == 'start':
                await self.chal_toggle(ctx, settings.config["challenges"]["monthly-challenge-signup"], settings.config["challenges"]["monthly-challenge-participant"])
                await channel.send(f'{role.mention} the new monthly challenge has started! Please be sure to grab the role again to be signed up for the next one')
            if action == 'stop':
                await self.chal_toggle(ctx, settings.config["challenges"]["monthly-challenge-participant"], settings.config["challenges"]["monthly-challenge-winner"])
                database.conn.execute(text(f'update challenge_data set historical = 1 where challenge_name = \'monthly\''))
        if challenge == 'yearly':
            if action == 'start':
                await self.chal_toggle(ctx, settings.config["challenges"]["yearly-challenge-signup"], settings.config["challenges"]["yearly-challenge-participant"])
            if action == 'stop':
                await self.chal_toggle(ctx, settings.config["challenges"]["yearly-challenge-participant"], settings.config["challenges"]["2021-challenge-winner"])
                database.conn.execute(text(f'update challenge_data set historical = 1 where challenge_name = \'yearly\''))
        if challenge == 'deadpool':
            if action == 'start':
                await self.chal_toggle(ctx, settings.config["challenges"]["deadpool-signup"], settings.config["challenges"]["deadpool-participant"])
            if action == 'stop':
                await self.chal_toggle(ctx, settings.config["challenges"]["deadpool-participant"], settings.config["challenges"]["deadpool-winner"])
                database.conn.execute(text(f'update challenge_data set historical = 1 where challenge_name = \'deadpool\''))

    @challenge.error
    async def challeneHandler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await utils.emoji(ctx, '❌')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please selected the challenge and/or action you would like to commit')
        else:
            print('\n--------', file=sys.stderr)
            print(f'Time      : {utils.timestr}', file=sys.stderr)
            print(f'Command   : {ctx.command}', file=sys.stderr)
            print(f'Message   : {ctx.message.content}', file=sys.stderr)
            print(f'Author    : {ctx.author}', file=sys.stderr)
            print(" ", file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command(name="participation", pass_context=True)
    async def participation_amount(self, ctx):
        """sends the current number of users with the M-Challenge participant role"""
        mpartcipants = len(await utils.role_pop(ctx, settings.config["challenges"]["monthly-challenge-participant"]))
        ypartcipants = len(await utils.role_pop(ctx, settings.config["challenges"]["yearly-challenge-participant"]))
        dparticipants = len(await utils.role_pop(ctx, settings.config["challenges"]["deadpool-participant"]))
        await utils.doembed(ctx, "Challenge statics", "Participation", f"\nMonthly Challenge Members left: {mpartcipants}\nYearly Challenge Members left: {ypartcipants}\nDeadpool Challenge Members Left: {dparticipants}", ctx.author, True)

    @commands.command(name='monthlychallenge')
    async def MonthlyChallenge(self, ctx):
        """command you use to give yourself the Monthly Challenge Signup role"""
        signup_role = ctx. guild.get_role(settings.config["challenges"]["monthly-challenge-signup"])
        await ctx.author.add_roles(signup_role)
        await utils.emoji(ctx)

    @commands.command(name="yearlychallenge")
    async def yearlychallenge(self, ctx):
        """Command you use to give yourself the Yearly Challenge Signup role"""
        signup_role = ctx.guild.get_role(settings.config["challenges"]["yearly-challenge-signup"])
        await ctx.author.add_roles(signup_role)
        await utils.emoji(ctx)

    @commands.command(name='deadpool')
    async def deadpool_signup(self, ctx):
        """Command you use to give yourself the Deadpool Signup role"""
        result = await database.userdata_select_query(ctx.author.id, False)
        if result[1] is not None and result[1] != 0:
            past_streak_time = datetime.fromtimestamp(result[1])
            if datetime.utcnow() > past_streak_time + timedelta(days=30):
                await ctx.channel.send("Cannot join because you're too far along in your streak. Congratulations!")
                return
        else:
            await ctx.channel.send("No streak data found. Please set your streak before entering the competition.")
            return
        signupRole = ctx.guild.get_role(settings.config["challenges"]["deadpool-signup"])
        await ctx.author.add_roles(signupRole)
        await utils.emoji(ctx)


    @tasks.loop(hours=12)
    async def update_challenge_data(self):
        monthly_data_query = text(
            f"select * from challenge_data where challenge_name = 'monthly' and CAST(updated_at as DATE) = UTC_DATE")
        monthly_data = database.conn.execute(monthly_data_query).fetchall()
        if len(monthly_data) == 0:
            role = self.client.get_guild(settings.config["serverId"]).get_role(settings.config["challenges"]["monthly-challenge-participant"])
            member_count = len(role.members)
            insert_record_query = text(f'insert into challenge_data(challenge_name, updated_at, participant_count) values(\'monthly\', UTC_TIMESTAMP(), {member_count})')
            database.conn.execute(insert_record_query)
        yearly_data_query = text(f"select * from challenge_data where challenge_name = 'yearly' and CAST(updated_at as DATE) = UTC_DATE")
        yearly_data = database.conn.execute(yearly_data_query).fetchall()
        if len(yearly_data) == 0:
            role = self.client.get_guild(settings.config["serverId"]).get_role(settings.config["challenges"]["yearly-challenge-participant"])
            member_count = len(role.members)
            insert_record_query = text(f'insert into challenge_data(challenge_name, updated_at, participant_count) values(\'yearly\', UTC_TIMESTAMP(), {member_count})')
            database.conn.execute(insert_record_query)
        deadpool_data_query = text(f"select * from challenge_data where challenge_name = 'deadpool' and CAST(updated_at as DATE) = UTC_DATE")
        deadpool_data = database.conn.execute(deadpool_data_query).fetchall()
        if len(deadpool_data) == 0:
            role = self.client.get_guild(settings.config["serverId"]).get_role(settings.config["challenges"]["deadpool-participant"])
            member_count = len(role.members)
            insert_record_query = text(f'insert into challenge_data(challenge_name, updated_at, participant_count) values(\'deadpool\', UTC_TIMESTAMP(), {member_count})')
            database.conn.execute(insert_record_query)

    # Code is implemented in Rust.

    @commands.command(name="produce_graph")
    async def produce_graph(self, challenge):
        """Create a graph of participants for a given challenge. Options are: monthly, yearly, or deadpool"""
        pass
    
def setup(client):
    client.add_cog(MonthlyChallenge(client))
