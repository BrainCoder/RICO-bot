import discord
from discord.ext import commands
from discord.ext.commands import Cog

import settings

from resources.reactRoles import r_dict


class reactroles(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None
        self.obj = r_dict


    def build_raw(self):
        raw_dict = []
        for key in self.obj:
            for sub_k in self.obj[key]:
                raw_dict.append(self.obj[key][sub_k])
        return raw_dict

    # Embed builder

    @commands.command(name="rr_autocreate")
    @commands.has_any_role(
        settings.config["staffRoles"]["developer"])
    async def rr_autocreate(self, ctx):
        for key in self.obj:
            if key == "streakGuide":
                await self.build_streakGuide(ctx, key)
            else:
                await self.build_embed(ctx)

    async def build_streakGuide(self, ctx, key):
        channel = ctx.guild.get_channel(settings.config["channels"]["streak-guide"])

        # info message
        embed = discord.Embed(title="React Roles", url="https://www.youtube.com/watch?v=dvWxtXgCD0Q", color=0x00dcff,
            description=f"This channel explains and highlights how to start and maintain your streak. To interact with the bot, both \
                covertly and overtly type all relevant commands in <#{settings.config['channels']['streaks']}>\n​")
        embed.set_author(name="NoPorn", url="https://discord.gg/CFR9bt", icon_url="https://cdn.discordapp.com/icons/519330541720436736/a_2bdbaecdd90c85cdc8e9108d8a8c5907.png?size=128")
        embed.add_field(name="Starting up your streak",
            value="To start your streak, type !relapse into the appropriate channel. This will start a timer that tracks your NoPMO streak. \
                This command can also be used to reset your streak if you relapse.  If you already have a NoPMO streak, you can add the \
                following arguments to the end of the !relapse command. \n\n```!relapse <DAY COUNT>\n!relapse <DAY COUNT> <HOUR COUNT>```\n \
                To update your streak, type !update in your preferred streak channel.", inline=False)
        embed.set_footer(text="NoPorn Companion was made by the NoPorn development team, please DM the bot for more information")
        await channel.send(embed=embed)

        # roles message
        embed = discord.Embed(title="Modes and Roles", color=0x00faa8)
        embed.set_author(name="NoPorn", url="https://discord.gg/CFR9bt", icon_url="https://cdn.discordapp.com/icons/519330541720436736/a_2bdbaecdd90c85cdc8e9108d8a8c5907.png?size=128")
        for sub_k in self.obj[key]:
            embed.add_field(name=f'{self.obj[key][sub_k][0]} - {sub_k}', value=self.obj[key][sub_k][2], inline=False)
        embed.set_footer(text="It is against server rules to harass/intimidate other users based on streak length or streak roles. We politely ask you to respect how other users intend to pursue their NoFap journey.")
        message = await channel.send(embed=embed)

        # add reactions

        for sub_k in self.obj[key]:
            emoji = self.obj[key][sub_k][0]
            print(emoji)
            await message.add_reaction(emoji)

    async def build_embed(self, ctx):
        pass

    # Emoji toggle detection

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.reaction(self, payload=payload, r_type='add')

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.reaction(self, payload=payload, r_type='remove')

    async def reaction(self, payload, r_type=None):
        raw_data = self.build_raw(self.obj)
        for entry in raw_data:
            if payload.channel_id == settings.config["channels"]["streak-guide"] or settings.config["channels"]["roles"]:
                for entry in raw_data:
                    if payload.emoji.name == entry[1]:
                        guild = self.client.get_guild(settings.config["serverId"])
                        user = guild.get_member(payload.user_id)
                        role = discord.utils.get(guild.roles, id=entry[2])
                        if r_type == 'remove':
                            await user.remove_role(role)
                        if r_type == 'add':
                            await user.add_role(role)


def setup(client):
    client.add_cog(reactroles(client))
