import discord
from discord.ext import commands

from sqlalchemy import text
import utils
import settings
from tabulate import tabulate

class ModeratorTools(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @commands.command(name="ngetstrikes", aliases=['sr', 'report'])
    @commands.has_any_role(
        settings.config["statusRoles"]["moderator"],
        settings.config["statusRoles"]["semi-moderator"]
        )
    async def report(self, ctx, user: discord.User = None, historical = 0):
        """NPC replacement for the !getstrikes command"""
        user_clause = ""
        if user is not None:
            user_clause = f' and recipient_id = {user.id}'
        prior_mute_queries = text(
            f'select me.recipient_id, met.mod_action_type, me.event_time, me.issuer_id, me.reason '
            f'from mod_event me '
            f'inner join mod_event_type met on me.event_type = met.mod_type_id where historical = {historical}'
            f' {user_clause} order by me.event_time desc limit 10')
        results = utils.conn.execute(prior_mute_queries)
        table = []
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
        await ctx.send("```" + tabulate(table,
                                        headers=["username", "action", "datetime", "moderator","reason"],
                                        ) + "```")
    @commands.command()
    @commands.has_any_role(
        settings.config["statusRoles"]["head-moderator"],
        settings.config["statusRoles"]["moderator"],
        )
    async def offline(self, ctx, role):
        """Lets you check which users are offline given the name of a role.
        If you want to check for a user with no roles, the phrase is \"empty\".
        This will then search for users with the default @everyone role.
        This is to ensure that @everyone is not mentioned.
        The command will also not take any roles with \"@\" symbols inside of them as a precaution."""
        everyone = False
        if '@' in role:
            await ctx.send(f'Please use the non-mentionable version of that role. '
                           f'If you\'re trying to check all offline users, unfortunately you can not.')
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
