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


def setup(client):
    client.add_cog(ModeratorTools(client))
