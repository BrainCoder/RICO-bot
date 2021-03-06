import database

import discord
from discord.ext import commands

from sqlalchemy import text
import settings
from tabulate import tabulate


class ModeratorTools(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @commands.command(name="getstrikes", aliases=['sr', 'gs', 'report'])
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"])
    async def report(self, ctx, user: discord.User = None, output_format="raw", historical="historical",
                     action="mute"):
        """NPC replacement for the !getstrikes command
        You can view a report for the most recent moderation actions on any user by just entering the command by itself.
        You can also choose either historical or current as the third argument to view acting strikes against a user.
        Format will default to raw output, but table option is available
        You can also request that the format be table, but will require prior arguments to also be filled in.
        The moderation action it queries against will be mutes(strikes) by default,
        but it can take the arguments of ban, kick,
        or will post all moderation actions if any other value is filled in there."""
        channel = self.client.get_channel(settings.config["channels"]["strike-board"])
        if historical.lower() == "historical":
            historical = 1
        elif historical.lower() == "current":
            historical = 0
        else:
            await ctx.send('Could not understand whether records should be historical or not. '
                           'Please enter either "historical" or "current" as the argument')
            return
        mod_action_clause = ""
        if action == "mute":
            mod_action_clause = " and me.event_type = 3"
        elif action == "kick":
            mod_action_clause = " and me.event_type = 2"
        elif action == "ban":
            mod_action_clause = " and me.event_type = 1"
        elif action == "cooldown":
            mod_action_clause = " and me.event_type = 5"
        elif action == "warn":
            mod_action_clause = " and me.event_type = 13"
        if output_format.lower() != "raw" and output_format.lower() != "table":
            await ctx.send('Format option only takes options "raw" or "table".')
            return
        user_clause = ""
        if user is not None:
            user_clause = f' and recipient_id = {user.id}'
        prior_mute_queries = text(
            f'select me.recipient_id, met.mod_action_type, me.event_time, me.issuer_id, me.reason '
            f'from mod_event me '
            f'inner join mod_event_type met on me.event_type = met.mod_type_id where historical = {historical}'
            f' {user_clause} {mod_action_clause} order by me.event_time desc limit 20')
        results = database.conn.execute(prior_mute_queries)
        table = []

        await self.extract_table_from_results(results, table, user)
        table_output = "```" + tabulate(table,
                                        headers=["username", "action", "datetime", "moderator", "reason"],
                                        ) + "```"
        raw_output = ""
        if user is None:
            raw_output += "For various users:\n"
        else:
            raw_output = f'For {user}:\n'
        raw_output = await self.build_raw_output(raw_output, table)
        await self.output_to_channel(channel, ctx, output_format, raw_output, table_output)

    async def extract_table_from_results(self, results, table, user):
        for result in results:
            output = result.values()
            if user is not None and self.client.get_user(user.id) is not None:
                output[0] = self.client.get_user(output[0]).name
            else:
                name = await self.client.fetch_user(output[0])
                output[0] = name
            output[2] = output[2].date()
            if self.client.get_user(output[3]) is not None:
                output[3] = self.client.get_user(output[3]).name
            else:
                name = await self.client.fetch_user(output[3])
                output[3] = name
            table.append(output)

    async def build_raw_output(self, raw_output, table, mod: bool = False):
        i = 0
        for row in table:
            i += 1
            raw_output += f'{str(i)}. {row[1]}'
            if mod:
                raw_output += f' for {row[3]}'
            else:
                raw_output += f' by {row[3]}'
            raw_output += f' on {row[2]}'
            if row[4] is not None:
                raw_output += f' for reason: {row[4]}'
            raw_output += "\n"
        return raw_output

    async def output_to_channel(self, channel, ctx, output_format, raw_output, table_output):
        if output_format == "table" and len(table_output) < 2000:
            await channel.send(table_output)
        else:
            if len(raw_output) > 2000:
                await ctx.send('Message exceeds 2,000 characters. Attempting to break into two messages.')
                midway_point = int(round(len(raw_output) / 2, 0))
                length = len(raw_output)
                first_half = raw_output[0:midway_point]
                last_half = raw_output[midway_point:length]
                if len(first_half) > 2000 or len(last_half) > 2000:
                    await ctx.send('Output is too long. Please contact a developer to see transcript.')
                else:
                    await channel.send(first_half)
                    await channel.send(last_half)
            else:
                await channel.send(raw_output)

    @commands.command(name="mreport", aliases=['mr'])
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"])
    async def mod_report(self, ctx, user: discord.User = None, output_format="raw", action="all"):
        """View moderation actions by a certain user. The role of the user is not taken into account.
        Format will default to raw output, but table option is available
        You can also request that the format be table, but will require prior arguments to also be filled in.
        The moderation action it queries against will be mutes(strikes) by default,
        but it can take the arguments of ban, kick,
        or will post all moderation actions if any other value is filled in there."""
        channel = self.client.get_channel(settings.config["channels"]["administration"])
        mod_action_clause = ""
        if action == "mute":
            mod_action_clause = "and me.event_type = 3"
        elif action == "kick":
            mod_action_clause = "and me.event_type = 2"
        elif action == "ban":
            mod_action_clause = "and me.event_type = 1"
        elif action == "warn":
            mod_action_clause = "and me.event_type = 13"
        else:
            mod_action_clause = "and me.event_type in (1, 2, 3, 13)"
        if output_format.lower() != "raw" and output_format.lower() != "table":
            await ctx.send('Format option only takes options "raw" or "table".')
            return
        if user is None:
            await ctx.send('Please select a user to view.')
            return
        user_clause = f'and issuer_id = {user.id}'
        prior_mute_queries = text(
            f'select me.issuer_id, met.mod_action_type, me.event_time, me.recipient_id, me.reason '
            f'from mod_event me '
            f'inner join mod_event_type met on me.event_type = met.mod_type_id where me.event_time > '
            f'(date_sub(curdate(), interval 14 day))'
            f' {user_clause} {mod_action_clause} order by me.event_time desc limit 20')
        results = database.conn.execute(prior_mute_queries)
        table = []

        await self.extract_table_from_results(results, table, user)
        table_output = "```" + tabulate(table,
                                        headers=["moderator", "action", "datetime", "recipient", "reason"],
                                        ) + "```"

        raw_output = f'For {user}:\n'
        raw_output = await self.build_raw_output(raw_output, table, True)
        await self.output_to_channel(channel, ctx, output_format, raw_output, table_output)

    @commands.command(name="removestrike", aliases=["rs", "rms"])
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"]
    )
    async def removestrike(self, ctx, user: discord.User, strike_number):
        """Removes strike of a user by number.
        If the command invoker is an admin, the number can also be set to \"all\"
        to remove all strikes for a particular user.
        Note that this ONLY works for regular mutes, as this is the only thing currently displayed
        when looking up strikes by default."""
        if user is None:
            await ctx.send("User is required.")
        elif strike_number == "all":
            admin_role = ctx.guild.get_role(settings.config["staffRoles"]["admin"])
            if admin_role in ctx.author.roles:
                query_to_remove_strikes = text(
                    f'update mod_event me set me.historical = 2 where me.recipient_id = {user.id} '
                    f'and me.event_type = 3 and historical = 1'
                )
                database.conn.execute(query_to_remove_strikes)
                await ctx.send("All strikes for " + user.mention + " should be gone.")
        else:
            query_to_find_strike = text(f'select * from mod_event me where me.recipient_id = {user.id} '
                                        f'and me.event_type = 3 and historical = 1 order by me.event_time desc')
            results = database.conn.execute(query_to_find_strike).fetchall()
            if (len(results) < int(strike_number)):
                await ctx.send("User does not have that many strikes.")
            else:
                id_of_strike_to_remove = results[int(strike_number)-1][0]
                query_to_remove_strikes = text(
                    f'update mod_event me set me.historical = 2 where me.recipient_id = {user.id} '
                    f'and me.event_type = 3 and event_id = {id_of_strike_to_remove}'
                )
                database.conn.execute(query_to_remove_strikes)
                await ctx.send("Strike number " + strike_number + " should be removed from the database.")


    @commands.command(name="offline")
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"])
    async def offline(self, ctx, role):
        """Lets you check which users are offline given the name of a role.
        If you want to check for a user with no roles, the phrase is \"empty\".
        This will then search for users with the default @everyone role.
        This is to ensure that @everyone is not mentioned.
        The command will also not take any roles with \"@\" symbols inside of them as a precaution."""
        everyone = False
        if '@' in role:
            await ctx.send('Please use the non-mentionable version of that role. '
                           'If you\'re trying to check all offline users, unfortunately you can not.')
            return
        role_to_index = None
        roles = ctx.guild.roles
        for role_in_guild in roles:
            if role.lower() == role_in_guild.name.lower():
                role_to_index = role_in_guild
                break
        if role == "empty":
            everyone = True
            role = "everyone"
            role_to_index = ctx.guild.roles[0]
        if role_to_index is None:
            await ctx.send(f'No role found named "{role}"')
            return
        members_with_role = []
        for member in ctx.guild.members:
            if role_to_index in member.roles and member.status is discord.Status.offline and not everyone:
                members_with_role.append(member)
            elif everyone and len(member.roles) == 1:
                members_with_role.append(member)
        if len(members_with_role) > 50:
            await ctx.send(f'Members offline with role "{role}": {len(members_with_role)}')
        elif len(members_with_role) == 0:
            await ctx.send(f'No members offline with role "{role}"')
        else:
            nicks = ""
            for member in members_with_role:
                nicks += member.display_name + "#" + member.discriminator + "\n"
            await ctx.send(f'Users offline:\n{nicks}')


def setup(client):
    client.add_cog(ModeratorTools(client))
