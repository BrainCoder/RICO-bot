from discord.ext import commands
from discord.ext.commands import Cog

import utils

from datetime import datetime, timedelta
import settings

class welcome(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @Cog.listener()
    async def on_member_join(self, member):
        with utils.engine.connect() as conn:
            channel = self.client.get_channel(settings.config["channels"]["welcome"])
            verify_previous_query = utils.userdata.select().where(utils.userdata.c.id == member.id)
            result = conn.execute(verify_previous_query).fetchone()
            if not result:
                await channel.send(
                    f'{member.mention} Welcome! Please go to <#{settings.config["channels"]["rules"]}> to read'
                    f' an overview of what this server is about. Go to <#{settings.config["channels"]["streak-guide"]}>'
                    f'and <#{settings.config["channels"]["roles-and-access"]}>'
                    f' to see the commands that you can use to assign yourself.')
                query = utils.userdata.insert(). \
                    values(id=member.id,
                           member_activation_date=int((datetime.now() +
                                timedelta(hours=settings.config["memberUpdateInterval"])).timestamp()))
                utils.conn.execute(query)
            else:
                await channel.send(
                    f'{member.mention} Welcome back! In case you need a reminder, you can go to '
                    f'<#{settings.config["channels"]["rules"]}> to read an overview of what this server is about. '
                    f'You can go to <#{settings.config["channels"]["streak-guide"]}> '
                    f'and <#{settings.config["channels"]["roles-and-access"]}>'
                    f' to see the commands that you can use to assign yourself.')
                if result[8] == 1: # muted
                    mute_role = member.guild.get_role(settings.config["statusRoles"]["muted"])
                    await member.add_roles(mute_role)
                elif result[9] == 1: # double-muted
                    double_mute_role = member.guild.get_role(settings.config["statusRoles"]["double-muted"])
                    await member.add_roles(double_mute_role)


def setup(client):
    client.add_cog(welcome(client))
