import utils
import database

from discord.ext import commands
from discord.ext.commands import Cog

import settings
import asyncio
import nest_asyncio


class Extra(commands.Cog):

    def __init__(self, client):
        nest_asyncio.apply()
        self.client = client
        self.afk_users = asyncio.run(self.build_afk_list())

    async def build_afk_list(self):
        afk_users = []
        rows = await database.userdata_select_query()
        for row in rows:
            if row[12] == 1:
                afk_users.append(row[0])
        return afk_users

    @commands.command(name='afk')
    @commands.has_any_role(
        settings.config["staffRoles"]["admin"],
        settings.config["staffRoles"]["head-moderator"],
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["trial-mod"],
        settings.config["statusRoles"]["vip"],
        settings.config["statusRoles"]["boost-vip"],
        settings.config["statusRoles"]["member"])
    async def afk(self, ctx, *, message: str = None):

        # If the author isnt already in afk_users list
        if ctx.author.id not in self.afk_users:

            nickname = 0

            # If their nickanme is the same as their display name
            if ctx.author.name != ctx.author.display_name:
                nickname = 1

            # Update userdata table
            await database.userdata_update_query(ctx.author.id, {'afk': 1})

            # Insert AFK event into afk_event table
            await database.afk_event_insert(ctx.author.id, ctx.author.display_name, nickname, message)

            # Add the user id to the afk_users list
            self.afk_users.append(ctx.author.id)

            if "[AFK]" not in ctx.author.display_name:

                # Attempt to change the username
                try:
                    await ctx.author.edit(nick=f'[AFK] {ctx.author.display_name}')
                except:
                    await ctx.send('failed to change nickname')

            await utils.emoji(ctx)


    @Cog.listener()
    async def on_message(self, message):

        # Check the message author is not a bot
        if not await utils.in_roles(message.author, settings.config["statusRoles"]["bot-role"]):

            # Check that there are AFK users
            if self.afk_users is not None:

                # Check if the autor is in AFK users && that the message isnt an AFK command
                if message.author.id in self.afk_users and "!afk" not in message.content:

                    # Check if the message was not in staff channel
                    if not await utils.in_staff_channel(message.channel.id):

                        # Update the user date to say the user is not AFK
                        await database.userdata_update_query(message.author.id, {'afk': 0})

                        try:
                            # Select the current AFK event entry
                            rows = await database.afk_event_select(message.author.id, True)
                            print(rows)

                            # If the user had a nickname
                            if rows[4] == 1:
                                await message.author.edit(nick=rows[3])
                            else:
                                await message.author.edit(nick=None)
                        except:
                            await message.channel.send('failed to change nickname')
                        
                        # Update the most recent afk event to be historical
                        await database.afk_event_update(message.author.id)

                        # Rebuild the afk_users list
                        self.afk_users = await self.build_afk_list()

                        # Inform user they are no longer afk
                        await message.channel.send(f'{message.author.mention} you are no longer afk')

                # If the author wasnt afk do this
                else:

                    # If the there are mentions in the message
                    if len(message.mentions) > 0:

                        # Loop through the mentions
                        for mention in message.mentions:

                            # If the mention user is afk do this:
                            if mention.id in self.afk_users:
                                
                                row = await database.afk_event_select(mention.id, True)
                                afk_message = row[2]
                                if afk_message is None:
                                    await message.channel.send(f'{mention} is currently AFK')
                                else:
                                    await message.channel.send(f'{mention} is currently afk with the message "{afk_message}"')

def setup(client):
    client.add_cog(Extra(client))
