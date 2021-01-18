import discord
from discord.ext import commands
from discord.ext.commands import Cog

import settings
import json


class reactroles(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None
        self.obj = self.getJson("resources/reactRoles.json")

    def getJson(self, path):
        with open(path, 'r') as fp:
            return json.load(fp)

    def build_raw(self, obj):
        raw_dict = []
        for key in obj:
            for sub_k in obj[key]:
                raw_dict.append(obj[key][sub_k])
        return raw_dict

    async def reaction(self, payload, r_type=None):
        raw_data = await self.build_raw(self.obj)
        for entry in raw_data:
            if payload.channel.id == settings.config["channels"]["streak-guide"] or settings.config["channels"]["roles"]:
                for entry in raw_data:
                    if payload.emoji.name == entry[1]:
                        guild = self.client.get_guild(settings.config["serverId"])
                        user = guild.get_member(payload.user_id)
                        role = discord.utils.get(guild.roles, id=entry[2])
                        if r_type == 'remove':
                            await user.remove_role(role)
                        if r_type == 'add':
                            await user.add_role(role)


    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await reactroles.reaction(self, payload=payload, r_type='add')

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await reactroles.reaction(self, payload=payload, r_type='remove')

def setup(client):
    client.add_cog(reactroles(client))
