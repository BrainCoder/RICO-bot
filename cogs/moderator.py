import discord
from discord.ext import commands

from sqlalchemy import text
import utils
import settings
from tabulate import tabulate  # TODO: Mention IN PR That this is a new library that must be installed.


class ModeratorTools(commands.Cog):

    @commands.command()
    @commands.has_any_role(settings.config["statusRoles"]["moderator"])
    async def report(self, ctx, user: discord.User):
        prior_mute_queries = text(
            f'select me.recipient_id, met.mod_action_type, me.event_time, me.reason from mod_event me inner join mod_event_type met on me.event_type = met.mod_type_id where'
            f' historical = 1 and recipient_id = 103128485295316992 limit 10')
        results = utils.conn.execute(prior_mute_queries)
        table = []
        for result in results:
            output = result.values()
            output[0] = self.client.get_user(output[0]).name
            table.append(output)
        len_of_tabulate = len(tabulate(table))
        await ctx.send("```" + tabulate(table, headers=["username", "action", "datetime", "reason"]) + "```")


def setup(client):
    client.add_cog(ModeratorTools(client))
