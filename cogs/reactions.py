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
        self.sguide = self.client.get_channel(settings.config["channels"]["streak-guide"])
        self.rolesc = self.client.get_channel(settings.config["channels"]["roles"])
        self.invite = settings.config["invite"]

    def build_raw(self):
        raw_dict = []
        for key in self.obj:
            for sub_k in self.obj[key]:
                raw_dict.append(self.obj[key][sub_k])
        return raw_dict


    @commands.command(name="rr_autocreate")
    @commands.has_any_role(
        settings.config["staffRoles"]["developer"])
    async def rr_autocreate(self, ctx):
        await self.sguide.purge(limit=300)
        await self.rolesc.purge(limit=300)
        await self.intro_message(ctx)
        for key in self.obj:
            if key == "streakGuide":
                await self.build_streakGuide(ctx, key)
            else:
                await self.build_embed(ctx, key)

    async def intro_message(self, ctx):
        embed = discord.Embed(title="Streak Guide", url="https://www.youtube.com/watch?v=dvWxtXgCD0Q", color=0x00dcff,
            description=f"This channel explains and highlights how to start and maintain your streak. To interact with the bot, both \
                covertly and overtly type all relevant commands in <#{settings.config['channels']['streaks']}>\n​")
        embed.set_author(name=ctx.guild.name, url=self.invite, icon_url=ctx.guild.icon_url)
        embed.add_field(name="Starting up your streak",
            value="To start your streak, type !relapse into the appropriate channel. This will start a timer that tracks your NoPMO streak. \
        This command can also be used to reset your streak if you relapse.  If you already have a NoPMO streak, you can add the \
        following arguments to the end of the !relapse command. \n\n```!relapse <DAY COUNT>\n!relapse <DAY COUNT> <HOUR COUNT>```\n \
        To update your streak, type !update in your preferred streak channel.", inline=False)
        embed.set_footer(text="NoPorn Companion was made by the NoPorn development team, please DM the bot for more information")
        await self.sguide.send(embed=embed)

        mod_role = ctx.guild.get_role(settings.config["staffRoles"]["moderator"])
        embed = discord.Embed(title="Roles & Access", url="https://www.youtube.com/watch?v=hv-ODnbbP7U", color=0x00dcff)
        embed.set_author(name=ctx.guild.name, url=self.invite, icon_url=ctx.guild.icon_url)
        embed.add_field(name='Getting your roles',
            value=f"Welcome to the Roles & Access channel. This is where you grab all relevant roles that caters to your interests. If you have any questions, please ping a {mod_role.mention}.\n \
        \nTo claim your role, simply react with the corresponding emoji.")
        embed.set_footer(text="NoPorn Companion was made by the NoPorn development team, please DM the bot for more information")
        await self.rolesc.send(embed=embed)

    async def build_streakGuide(self, ctx, key):
        embed = discord.Embed(title="Modes and Roles", color=0x00faa8)
        embed.set_author(name=ctx.guild.name, url=self.invite, icon_url=ctx.guild.icon_url)
        for sub_k in self.obj[key]:
            embed.add_field(name=f'{self.obj[key][sub_k][0]} - {sub_k}', value=self.obj[key][sub_k][2], inline=False)
        embed.set_footer(text="It is against server rules to harass/intimidate other users based on streak length or streak roles. We politely ask you to respect how other users intend to pursue their NoFap journey.")
        message = await self.sguide.send(embed=embed)
        await self.add_emoji(message, key)

    async def build_embed(self, ctx, key):
        string = ""
        embed = discord.Embed(title=key, url="https://pngimg.com/uploads/trollface/trollface_PNG31.png", color=0x00faa8)
        embed.set_author(name=ctx.guild.name, url=self.invite, icon_url=ctx.guild.icon_url)
        for sub_k in self.obj[key]:
            entry = f"{self.obj[key][sub_k][0]} - {sub_k}\n"
            string = string + entry
        string = string + "​"
        embed.add_field(name="Pick one of these", value=string, inline=False)
        if key == "Utility":
            embed.add_field(name="Please Note", value="It is against server rules to troll or harras member when they are seeking help, this is refrenced in rule 4.", inline=False)
        elif key == "Gender":
            embed.add_field(name="Please Note", value="It is against server rules to take the wrong gender role, regardlles of the reason, this is refrenced in rule 12.", inline=False)
        elif key == "Religion":
            embed.add_field(name="Please Note", value="While it is not against server rules to take roles of a religion of which you do not subscribe, we poltiely ask if you do please respect the beleifs of the users of that relgions channel.", inline=False)
        elif key == "Location":
            embed.add_field(name="Please Note", value="It is against the server rules to harass and intimidate other users based on their country of origin (Rule 8). Please do not attack another user based on the roles they adopt.", inline=False)
        elif key == "Hobbies":
            embed.add_field(name="Please Note", value="The fitness channel holds a weekly event called physique Friday. During this time, certain members could be exposed to triggering material. If this personally affects you, it is the staff team’s recommendation that you do not take the fitness role.", inline=False)
        elif key == "Misc":
            embed.add_field(name="Please Note", value="Be self-aware of what you say and the content you post inside the memes channel, due to Discord TOS.", inline=False)
        message = await self.rolesc.send(embed=embed)
        await self.add_emoji(message, key)

    async def add_emoji(self, message, key):
        for sub_k in self.obj[key]:
            emoji = self.obj[key][sub_k][0]
            await message.add_reaction(emoji)


    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.reaction(payload=payload, r_type='add')

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.reaction(payload=payload, r_type='remove')

    async def reaction(self, payload, r_type=None):
        if payload.channel_id == settings.config["channels"]["streak-guide"] or settings.config["channels"]["roles"]:
            if payload.user_id != settings.config["botId"]:
                raw_data = self.build_raw()
                for entry in raw_data:
                    if payload.emoji.name == entry[0]:
                        guild = self.client.get_guild(settings.config["serverId"])
                        user = guild.get_member(payload.user_id)
                        role = guild.get_role(entry[1])
                        if r_type == 'remove':
                            await user.remove_roles(role)
                        if r_type == 'add':
                            await user.add_roles(role)


def setup(client):
    client.add_cog(reactroles(client))
