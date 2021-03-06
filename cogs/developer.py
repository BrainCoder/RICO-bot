import utils
import database

import settings

from discord.ext import commands


class DeveloperTools(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.devlogs = self.client.get_channel(settings.config["channels"]["devlog"])

    @commands.command(name="cog", aliases=["cogs"])
    @commands.has_any_role(
        settings.config["staffRoles"]["head-dev"],
        settings.config["staffRoles"]["developer"],
    )
    async def cog(self, ctx, action, *args):
        """Command to manually toggle cogs. For action use either\n**load** - load the cog\n**unload** - unload the cog\n**reload** - reload the cog"""
        for arg in args:
            try:
                ignore = False
                if action == "load":
                    self.client.load_extension(f"cogs.{arg}")
                elif action == "unload":
                    if arg != "developer":
                        self.client.unload_extension(f"cogs.{arg}")
                elif action == "reload":
                    self.client.reload_extension(f"cogs.{arg}")
                else:
                    await ctx.send(f"{action} is not a valid argument")
                    ignore = True
            except commands.errors.ExtensionNotLoaded:
                await ctx.send(f"{arg} is not a cog")
            else:
                if not ignore:
                    await self.devlogs.send(
                        f"{utils.timestr}`{arg}` {action}ed manually"
                    )
        await utils.emoji(ctx)


    @commands.command(name="ping")
    async def ping(self, ctx):
        """Check the latency of the bot"""
        await ctx.send(f"pong! Latency is {self.client.latency * 1000}ms")

    @commands.command(name="get")
    @commands.has_any_role(
        settings.config["staffRoles"]["head-dev"],
        settings.config["staffRoles"]["developer"],
    )
    async def get(self, ctx, _type, id):
        """Developer tool used to get roles or channels based on ids"""
        if _type == "channel":
            await self.getchannel(ctx, id)
        if _type == "role":
            await self.getrole(ctx, id)
        if _type == "user":
            await self.getuser(ctx, id)

    async def getchannel(self, ctx, id):
        channel = ctx.guild.get_channel(int(id))
        try:
            await ctx.send(f"{channel.mention}")
        except:
            await ctx.send("This channel does not exist")

    async def getrole(self, ctx, id):
        obj_role = ctx.guild.get_role(int(id))
        try:
            await ctx.send(f"{obj_role.mention}")
        except:
            await ctx.send("This role does not exist")

    async def getuser(self, ctx, id):
        user = ctx.guild.get_member(id)
        try:
            await ctx.send(user.name)
        except:
            await ctx.send("This user does not exist")

    @commands.command(name="verifyintegrity", aliases=["vi", "verify"])
    @commands.has_any_role(
        settings.config["staffRoles"]["head-dev"],
        settings.config["staffRoles"]["developer"],
    )
    async def verifyintegrity(self, ctx, action):
        """command does one of two things based on the arguments given\n**database** - Ensures that all users currently in the server are inside the database, and adds them if not.\n**memeber** - Verifies the member status using the guild as the source of truth
        of users within the guild that the command was typed in.
        Note this can not track users who are not in the guild that this was called in, but also might have
        a member value set."""
        if action == "database":
            await utils.emoji(ctx, "???")
            await self.devlogs.send(
                f"{utils.timestr}databse integrity verified by {ctx.author.name}"
            )
            await self.vi_db(ctx)
        elif action == "member":
            await utils.emoji(ctx, "???")
            await self.devlogs.send(
                f"{utils.timestr}member integrity verified by {ctx.author.name}"
            )
            await self.vi_member(ctx)

    async def vi_db(self, ctx):
        current_users = len(
            database.conn.execute(database.userdata.select()).fetchall()
        )
        for user in ctx.guild.members:
            result = await database.userdata_select_query(user.id, False)
            if not result and not user.bot:
                await database.userdata_insert_query(user.id)
        new_count = len(database.conn.execute(database.userdata.select()).fetchall())
        await ctx.channel.send(
            "The old amount of users was "
            + str(current_users)
            + "\nThe new amount of users is "
            + str(new_count)
        )

    async def vi_member(self, ctx):
        members_added = []
        members_lost = []
        missing_members = []
        for user in ctx.guild.members:
            if not user.bot:
                result = await database.userdata_select_query(user.id, False)
                if result:
                    member_role = ctx.guild.get_role(
                        settings.config["statusRoles"]["member"]
                    )
                    if member_role in user.roles and result[8] == 0:

                        await database.userdata_update_query(user.id, {"member": 1})
                        members_added.append(user.name)

                    elif member_role not in user.roles and result[8] == 1:

                        await database.userdata_update_query(user.id, {"member": 0})
                        members_lost.append(user.name)
                else:
                    missing_members.append(user.name)
        await ctx.send(
            f"Amount of users added: {str(len(members_added))}\n"
            f"Amount of users lost: {str(len(members_lost))}\n"
            f"Amount of users missing: {str(len(missing_members))}"
        )

        if len(missing_members) > 0:
            await self.vi_db

def setup(client):
    client.add_cog(DeveloperTools(client))
