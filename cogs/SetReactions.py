import discord
from discord.ext import commands
from discord.ext.commands import Cog

import settings

s_guide = '773732031771181076'
util = '774274027601920010'
gender = '774274069821784104'
religion = '774274107247296523'
location = '774274252941426688'
hobbies = '774274285430636604'
misc = '774274316883591168'

reaction_roles = [
    (s_guide, (settings.config["modeRoles"]["classicmode"]), '🟢'),
    (s_guide, (settings.config["modeRoles"]["hardmode"]), '🟡'),
    (s_guide, (settings.config["modeRoles"]["monkmode"]), '🔴'),

    (util, (settings.config["otherRoles"]["helper"]), '🆘'),
    (util, (settings.config["otherRoles"]["support-group"]), '⚕️'),
    (util, (settings.config["otherRoles"]["monthly-challenge"]), '🎮'),
    (util, (settings.config["otherRoles"]["acc-partner"]), '👥'),
    (util, (settings.config["otherRoles"]["urge-killer"]), ':cockroach:'),
    (util, (settings.config["modeRoles"]["anon-streak"]), '🕵️'),
    (util, (settings.config["otherRoles"]["virgin"]), ':regional_indicator_v:'),
    (util, (settings.config["otherRoles"]["cavemanmode"]), '📵'),
    (util, (settings.config["otherRoles"]["retention"]), ':regional_indicator_r:'),

    (gender, (settings.config["genderRoles"]["male"]), '♂️'),
    (gender, (settings.config["genderRoles"]["female"]), '♀️'),

    (religion, (settings.config["religionRoles"]['islam']), '☪️'),
    (religion, (settings.config["religionRoles"]['christianity']), '✝️'),
    (religion, (settings.config["religionRoles"]['judaism']), '🔯'),
    (religion, (settings.config["religionRoles"]['religious-else']), '♾️'),

    (location, (settings.config["continentRoles"]["antarctica"]), ':flag_aq:'),
    (location, (settings.config["continentRoles"]["oceania"]), ':flag_au:'),
    (location, (settings.config["continentRoles"]["north-america"]), ':flag_um:'),
    (location, (settings.config["continentRoles"]["south-america"]), ':flag_mx:'),
    (location, (settings.config["continentRoles"]["europe"]), ':flag_eu:'),
    (location, (settings.config["continentRoles"]["africa"]), ':flag_za:'),
    (location, (settings.config["continentRoles"]["asia"]), ':flag_cn:'),

    (hobbies, (settings.config["hobbies"]["hydrator"]), '💧'),
    (hobbies, (settings.config["otherRoles"]["productivity"]), '✍'),
    (hobbies, (settings.config["otherRoles"]["book-club"]), '📚'),
    (hobbies, (settings.config["hobbies"]["fitness"]), '🏋️‍♂️'),
    (hobbies, (settings.config["hobbies"]["chess"]), '♟️'),
    (hobbies, (settings.config["hobbies"]["discussions"]), '🗣️'),
    (hobbies, (settings.config["hobbies"]["relationships"]), '👫'),

    (misc, (settings.config["misc"]["memes"]), '🚽'),
    (misc, (settings.config["misc"]["media"]), '🗞️'),
    (misc, (settings.config["misc"]["polls"]), '🗳️'),
    (misc, (settings.config["misc"]["asylum"]), '🤯')]

class reactroles(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    async def reaction(self, payload, r_type=None):
        for reaction_info in reaction_roles:
            if payload.message_id == reaction_info[0]:
                if payload.emoji.name == reaction_info[2]:
                    guild = self.client.get_guild(settings.config["serverId"])
                    user = guild.get_member(payload.user_id)
                    role = discord.utils.get(guild.roles, id=reaction_info[1])
                    if r_type == 'remove':
                        await user.remove_roles(role)
                    if r_type == 'add':
                        await user.add_roles(role)

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await reactroles.reaction(self, payload=payload, r_type='add')

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await reactroles.reaction(self, payload=payload, r_type='remove')

def setup(client):
    client.add_cog(reactroles(client))
