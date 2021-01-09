import discord
from discord.ext import commands
from discord.ext.commands import Cog

import settings
import json

configFile = open('resources/reactRoles.json', 'r')
jsondata = configFile.read()
obj = json.loads(jsondata)


class reactroles(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    async def build_raw(self):
        raw_dict = []
        for category in obj:
            for sub_cat in category:
                raw_dict.append(sub_cat)
        return raw_dict

    async def reaction(self, payload, r_type=None):
        raw_data = await self.build_raw()
        for entry in raw_data:
            if payload.channel.id == obj["streakGuideChannel"] or obj["reactRolesChannel"]:
                for entry in raw_data:
                    if payload.emoji.name == entry[1]:
                        guild = self.client.get_guild(settings.config["serverId"])
                        user = guild.get_member(payload.user_id)
                        role = discord.utils.get(guild.roles, id=entry[2])
                        if r_type == 'remove':
                            await user.remove_role(role)
                        if r_type == 'add':
                            await user.add_role(role)

    async def build_embed(self, ctx, title, fname, fval):
        pass


    @commands.command(name='rr_autocreate')
    @commands.has_any_role(
        settings.config['staffRoles']['developer'])
    async def rr_autocreate(self, ctx, channel, title, fname, fval):
        channel = ctx.guild.get_channel(channel)
        await ctx.channel.purge(limit=100)
        for category in obj:
            embed = discord.Embed(title=title, url="https://www.youtube.com/watch?v=hv-ODnbbP7U", color=0x00dcff)
            embed.set_author(name="NoPorn", url="https://discord.gg/CFR9bt", icon_url="https://cdn.discordapp.com/icons/519330541720436736/a_2bdbaecdd90c85cdc8e9108d8a8c5907.png?size=128")
            embed.add_field(name=fname, value=fval, inline=False)
            embed.set_footer(text="NoPorn Companion was made by the NoPorn development team, please DM the bot for more information")
            await ctx.send(embed=embed)

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await reactroles.reaction(self, payload=payload, r_type='add')

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await reactroles.reaction(self, payload=payload, r_type='remove')

def setup(client):
    client.add_cog(reactroles(client))
