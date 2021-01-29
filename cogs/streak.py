import utils
import database

from discord.ext import commands
import discord
import settings
import asyncio
import traceback
import sys
from datetime import datetime, timedelta


class Streak(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    def getStreakString(self, total_streak_length):
        days, remainder = divmod(total_streak_length, 60*60*24)
        hours, remainder = divmod(remainder, 60*60)
        days = int(days)
        hours = int(hours)
        print(days, hours)
        daysStr = f'{days} day{"s" if days > 1 else ""}' if days > 0 else ''
        middleStr = ' and ' if days > 0 and hours > 0 else ''
        hoursStr = f'{hours} hour{"s" if hours != 1 else ""}' if hours > 0 else ''
        return [daysStr, middleStr, hoursStr]

    def getOwnedStreakRole(self, member):
        for role in utils.idData[member.guild.id]['streakRoles']:
            for memberRole in member.roles:
                if memberRole.id == utils.idData[member.guild.id]['streakRoles'][role]:
                    return utils.idData[member.guild.id]['streakRoles'][role]
        return None

    def getDeservedStreakRole(self, days, serverID):
        for role in utils.idData[serverID]['streakRoles']:
            if days < int(role) or int(role) == -1:
                return utils.idData[serverID]['streakRoles'][role]

    async def updateStreakRole(self, member, startingDate):
        days = (datetime.utcnow().today() - startingDate).days
        owned = self.getOwnedStreakRole(member)
        deserved = self.getDeservedStreakRole(days, member.guild.id)
        if owned == deserved:
            return
        if owned is not None:
            roleObj = member.guild.get_role(owned)
            await member.remove_roles(roleObj)
        roleObj = member.guild.get_role(deserved)
        await member.add_roles(roleObj)

    async def removeStreakRoles(self, author):
        for role in author.roles:
            id = author.guild.get_role(role.id).id
            if id in settings.config["streakRoles"].values():
                await author.remove_roles(role)
                return

    async def check_permitted_streak_set_amount(self, ctx, number):
        if (number > 30 and not await utils.in_roles(ctx.author, settings.config["statusRoles"]["vip"]) and
                number > 30 and not await utils.in_roles(ctx.author, settings.config["statusRoles"]["boost-vip"])):
            return -1
        elif number > 90 and not await utils.is_staff(ctx):
            return -1
        return number

    async def challenge(self, ctx, role):
        object_role = ctx.guild.get_role(role)
        await ctx.author.remove_roles(object_role)
        no = len(await utils.role_pop(ctx, role))
        if role == settings.config["challenges"]["monthly-challenge-participant"]:
            channel = ctx.guild.get_channel(settings.config["channels"]["monthly-challenge"])
            await channel.send(f'Monthly Challenge members left: {no}')
        elif role == settings.config["challenges"]["yearly-challenge-participant"]:
            channel = ctx.guild.get_channel(settings.config["channels"]["yearly-challenge"])
            await channel.send(f'Yearly Challenge members left: {no}')
        elif role == settings.config["challenges"]["deadpool-participant"]:
            channel = ctx.guild.get_channel(settings.config["channels"]["deadpool-challenge"])
            await channel.send(f'Deadpool memebers left: {no}')

    async def delayed_delete(self, message):
        await asyncio.sleep(5)
        await message.delete()


    @commands.command(name="relapse")
    @commands.check(utils.is_in_streak_channel)
    @commands.cooldown(3, 60, commands.BucketType.user)
    async def relapse(self, ctx, *args):
        """resets the users streak to day 0"""

        # Challenges

        Anon = await utils.in_roles(ctx.author, settings.config["modeRoles"]["anon-streak"])
        if Anon:
            await ctx.message.delete()
            await self.removeStreakRoles(ctx.author)
        if await utils.in_roles(ctx.author, settings.config["challenges"]["monthly-challenge-participant"]):
            await self.challenge(ctx, settings.config["challenges"]["monthly-challenge-participant"])
        if await utils.in_roles(ctx.author, settings.config["challenges"]["yearly-challenge-participant"]):
            await self.challenge(ctx, settings.config["challenges"]["yearly-challenge-participant"])
        if await utils.in_roles(ctx.author, settings.config["challenges"]["deadpool-participant"]):
            await self.challenge(ctx, settings.config["challenges"]["deadpool-participant"])
        if await utils.in_roles(ctx.author, settings.config["modeRoles"]["highest-streak"]):
            role = await ctx.server.get_role(settings.config["modeRoles"]["highest-streak"])
            await ctx.author.remove(role)

        # Decode the args

        maxDays = 365 * 10
        n_days = 0
        n_hours = 0
        if(len(args) > 0 and args[0].isnumeric() and maxDays > int(args[0]) >= 0):
            if (await self.check_permitted_streak_set_amount(ctx, int(args[0]))) == -1:
                message = await ctx.channel.send('You cannot set your streak this high without moderator help.')
                if Anon:
                    await self.delayed_delete(message)
                return
            n_days = int(args[0])
            if(len(args) > 1 and args[1].isnumeric() and 24 > int(args[1]) >= 0):
                n_hours = int(args[1])
            elif(len(args) > 1 and (not args[1].isnumeric() or not 24 > int(args[1]) >= 0)):
                message = await ctx.channel.send('The provided command arguments are not permitted.')
                if Anon:
                    await self.delayed_delete(message)
                return
        elif(len(args) > 0 and (not args[0].isnumeric() or not maxDays > int(args[0]) >= 0)):
            message = await ctx.channel.send('The provided command arguments are not permitted.')
            if Anon:
                await self.delayed_delete(message)
            return

        # Database update
        current_starting_date = datetime.utcnow().today() - timedelta(days=n_days, hours=n_hours)
        rows = await database.userdata_select_query(ctx.author.id)

        # If they have a previous streak
        if(rows[0]['last_relapse'] is not None):
            last_starting_date = utils.to_dt(rows[0]['last_relapse'])
            total_streak_length = (current_starting_date - last_starting_date).total_seconds()

            # If total streak is longer than 1min
            if total_streak_length > 60:
                [daysStr, middleStr, hoursStr] = self.getStreakString(total_streak_length)
                totalHours, _ = divmod(total_streak_length, 60*60)

                # Insert data into the past_streaks table

                await database.past_insert_query(ctx.author.id, totalHours)

                await database.userdata_update_query(ctx.author.id, {'last_relapse': current_starting_date.timestamp()})
                if hoursStr is not None:
                    message = await ctx.channel.send(f'Your streak was {daysStr}{middleStr}{hoursStr} long.')
                else:
                    message = await ctx.channel.send('Your streak was less than an hour long')
                if not Anon:
                    await self.updateStreakRole(ctx.author, current_starting_date)
                    await ctx.send('Don’t be dejected')
                    await utils.get_emergency_picture(ctx, relapse=True)
                if Anon:
                    await self.delayed_delete(message)

        # If they dont have a previous streak
        if(rows[0]['last_relapse'] is None or total_streak_length <= 60):
            await database.userdata_update_query(ctx.author.id, {'last_relapse': current_starting_date.timestamp()})
            if not Anon:
                await self.updateStreakRole(ctx.author, current_starting_date)
            message = await ctx.channel.send('Streak set successfully.')
            if Anon:
                await self.delayed_delete(message)
    @relapse.error
    async def relapse_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('That command cannot be used in this channel')
        elif isinstance(error, commands.CommandOnCooldown):
            better_time = await utils.convert_from_seconds(error.retry_after)
            await ctx.send(content=f'This command is on cooldown. Please wait {better_time}', delete_after=5)
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


    @commands.command(name="update")
    @commands.check(utils.is_in_streak_channel)
    @commands.cooldown(3, 900, commands.BucketType.user)
    async def update(self, ctx):
        """updates the users streak"""
        highest_role = ctx.guild.get_role(settings.config["modeRoles"]["highest-streak"])
        Anon = await utils.in_roles(ctx.author, settings.config["modeRoles"]["anon-streak"])
        if Anon:
            await ctx.message.delete()
            await self.removeStreakRoles(ctx.author)
        rows = await database.userdata_select_query(ctx.author.id)
        if(len(rows) and rows[0]['last_relapse'] is not None):
            last_starting_date = utils.to_dt(rows[0]['last_relapse'])
            total_streak_length = (datetime.utcnow().today() - last_starting_date).total_seconds()
            [daysStr, middleStr, hoursStr] = self.getStreakString(total_streak_length)
            past_streaks_rows = await database.past_select_query(ctx.author.id)
            if past_streaks_rows is not None:
                streaks = []
                for row in past_streaks_rows:
                    days = row[2]
                    streaks.append(days)
                if max(streaks) < total_streak_length:
                    highest = True
            else:
                if not Anon:
                    await ctx.author.add_role(highest_role)
            if not Anon:
                await self.updateStreakRole(ctx.author, last_starting_date)
                if highest:
                    await ctx.author.add_role(highest_role)
            message = await ctx.channel.send(f'Your streak is {daysStr}{middleStr}{hoursStr} long.')
            if Anon:
                await self.delayed_delete(message)
        else:
            message = await ctx.channel.send("No data about you available do !relapse .")
            if Anon:
                await self.delayed_delete(message)
    @update.error
    async def update_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('That command cannot be used in this channel')
        elif isinstance(error, commands.CommandOnCooldown):
            better_time = await utils.convert_from_seconds(error.retry_after)
            await ctx.send(content=f'This command is on cooldown. Please wait {better_time}', delete_after=5)
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


    @commands.command(name="fstreak")
    @commands.has_any_role(
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["head-moderator"])
    async def set_streak(self, ctx, member: discord.Member, *args):
        """forces someone's streak to a certain time.

        Takes the same arguments as if you were to set your streak for the first time in relapse.
        second argument must be less than 24 hours, and a user that is already in the database must be provided."""
        if member is None:
            await ctx.channel.send("You need to specify a user.")
        new_starting_date = datetime.utcnow().today()
        if len(args) >= 1:
            n_days = int(args[0])
            new_starting_date = new_starting_date - timedelta(days=n_days)
        if len(args) >= 2 and int(args[1]) < 24:
            n_hours = int(args[1])
            new_starting_date = new_starting_date - timedelta(hours=n_hours)
        elif len(args) >= 2 and int(args[1]) > 24:
            await ctx.channel.send("Please send a value less than or equal to 24 hours")
            return
        await database.userdata_update_query(member.id, {'last_relapse': new_starting_date.timestamp()})
        await self.updateStreakRole(ctx.author, new_starting_date)
        await ctx.channel.send("Streak set successfully.")


    @commands.command(name="stats")
    @commands.cooldown(3, 900, commands.BucketType.user)
    async def ps_stats(self, ctx):
        streaks = []

        # Get current streak and place it in the streaks list
        userdata_rows = await database.userdata_select_query(ctx.author.id)
        if(userdata_rows[0]['last_relapse'] is not None):
            last_starting_date = utils.to_dt(userdata_rows[0]['last_relapse'])
            total_streak_length = (datetime.utcnow().today() - last_starting_date).total_seconds()

        # Get the past streaks data from the databse
        past_streaks_rows = await database.past_select_query(ctx.author.id)
        if past_streaks_rows is not None:
            for row in past_streaks_rows:
                days = row[2]/24
                streaks.append(days)
            streaks.append(total_streak_length)
        total_relapses = len(streaks)

        # If they have a previous streak
        if total_relapses != 0:
            avg = sum(streaks) / total_relapses
            highest = max(streaks)
            await utils.doembed(ctx, 'Past Streaks', 'Stats', f'Total Relapses: {total_relapses}\nHighest streak: {int(round(highest))}\nAverage Streak: {int(round(avg))}', ctx.author, True)

        # If they dont have a previous streak
        else:
            await ctx.send('There current is no data on your past streaks to calculate statistics for.')


def setup(client):
    client.add_cog(Streak(client))
