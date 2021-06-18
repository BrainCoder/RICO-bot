import database

from discord.ext import commands
from discord.ext.commands import Cog

from datetime import datetime, timedelta
import settings


class welcome(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @Cog.listener()
    async def on_member_join(self, member):
        with database.engine.connect() as conn:
            verify_previous_query = database.userdata.select().where(database.userdata.c.id == member.id)
            result = conn.execute(verify_previous_query).fetchone()
            if not result:
                query = database.userdata.insert(). \
                    values(id=member.id,
                           member_activation_date=int((datetime.utcnow() +
                                timedelta(hours=settings.config["memberUpdateInterval"])).timestamp()))
                conn.execute(query)
            else:
                if result[5] == 1:
                    mute_role = member.guild.get_role(settings.config["statusRoles"]["muted"])
                    await member.add_roles(mute_role)
                if result[6] == 1:
                    double_mute_role = member.guild.get_role(settings.config["statusRoles"]["double-muted"])
                    await member.add_roles(double_mute_role)


def setup(client):
    client.add_cog(welcome(client))
