import os
import gitlab
import re
import settings
import traceback
import sys

from discord import File
from discord.ext import commands
import utils
from sqlalchemy import update
from re import search

async def vi_db(ctx):
    new_entries = 0
    current_users = len(utils.conn.execute(utils.userdata.select()).fetchall())
    for user in ctx.guild.members:
        query = utils.userdata.select().where(utils.userdata.c.id == user.id)
        result = utils.conn.execute(query).fetchone()
        if not result and not user.bot:
            query = utils.userdata.insert(). \
                values(id=user.id)
            utils.conn.execute(query)
            new_entries += 1
    new_count = len(utils.conn.execute(utils.userdata.select()).fetchall())
    await ctx.channel.send("The old amount of users was " + str(current_users) + \
                        "\nThe new amount of users is " + str(new_count))

async def vi_member(ctx):
    members_added = []
    members_lost = []
    missing_members = []
    for user in ctx.guild.members:
        query = utils.userdata.select().where(utils.userdata.c.id == user.id)
        result = utils.conn.execute(query).fetchone()
        if result:
            member_role = ctx.guild.get_role(settings.config["statusRoles"]["member"])
            if member_role in user.roles and result[11] == 0:
                user_data_query = update(utils.userdata).where(utils.userdata.c.id == user.id) \
                    .values(member=1)
                utils.conn.execute(user_data_query)
                members_added.append(user.name)
            elif member_role not in user.roles and result[11] == 1:
                user_data_query = update(utils.userdata).where(utils.userdata.c.id == user.id) \
                    .values(member=0)
                utils.conn.execute(user_data_query)
                members_lost.append(user.name)
        else:
            missing_members.append(user.name)
    if len(missing_members) > 0:
        dev_log_channel = ctx.guild.get_channel(settings.config["channels"]["devlog"])
        await dev_log_channel.send(f'The following users were not in the database: '
                                f'{",".join(missing_members)}')
    await ctx.send(f'Amount of users added: {str(len(members_added))}\n'
                f'Amount of users lost: {str(len(members_lost))}')

class DeveloperTools(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None
        self.url = 'https://gitlab.com/'
        self.authkey = sys.argv[3]
        self.project_name = settings.config["gitlabName"]
        self.project = None
        server = gitlab.Gitlab(self.url, self.authkey, api_version=4, ssl_verify=True)
        self.project = server.projects.get(self.project_name)

    @commands.command(name='test')
    async def test(self, ctx):
        await utils.doembed(ctx, 'aname', 'fname', 'fval')

    @commands.command(name="checklist", aliases=['cl'])
    @commands.has_any_role(
        settings.config["staffRoles"]["moderator"],
        settings.config["staffRoles"]["semi-moderator"],
        settings.config["staffRoles"]["developer"])
    async def cl(self, ctx, *, raw):
        """Add the message to the dev team job-board"""
        rawregex = r"[a-zA-Z0-9] - [a-zA-Z0-9]"
        if search(rawregex, raw):
            pattern = re.compile(" - ")
            broken = pattern.split(raw)
            if "-" in broken[1]:
                await ctx.send('Please do not include `-` in your job description')
            else:
                self.project.issues.create({'title': f'{broken[0]}', 'description': f'{ broken[1]}\n\nIssue created by: {ctx.message.author.name}'})
                await utils.emoji(ctx, '✅')
        else:
            await ctx.send('Please enter your job in the following format\n```!cl {job title} - {job description}```')

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Check the latency of the bot"""
        await ctx.send(f'pong! Latency is {self.client.latency * 1000}ms')

    @commands.command(name="getchannel")
    @commands.has_any_role(
        settings.config["staffRoles"]["developer"])
    async def getchannel(self, ctx, id):
        """Find a channel with the channel ID"""
        channel = ctx.guild.get_channel(int(id))
        await ctx.send(f'{channel}')

    @commands.command(name='repeat', aliases=['mimic', 'copy'])
    @commands.has_any_role(
        settings.config["staffRoles"]["developer"])
    async def do_repeat(self, ctx, *, inp: str):
        """repeats the input you give it"""
        await ctx.send(inp)
    @do_repeat.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'inp':
                await ctx.send("You forgot to give me input to repeat!")
            else:
                print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
                traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command(name='verifyintegrity', aliases=['vi', 'verify'])
    @commands.has_any_role(
        settings.config["staffRoles"]["developer"])
    async def verifyintegrity(self, ctx, action):
        """command does one of two things based on the arguments given\n**database** - Ensures that all users currently in the server are inside the database, and adds them if not.\n**memeber** - Verifies the member status using the guild as the source of truth
        of users within the guild that the command was typed in.
        Note this can not track users who are not in the guild that this was called in, but also might have
        a member value set."""
        if action == 'database':
            await utils.emoji(ctx, '✅')
            await vi_db(ctx)
        elif action == 'member':
            await utils.emoji(ctx, '✅')
            await vi_member(ctx)

    @commands.command(name='error')
    @commands.has_any_role(
        settings.config["staffRoles"]["developer"])
    async def errorlog(self, ctx, action=None):
        if action is None:
            path = '/root/.pm2/logs/NPC-error.log'
            if os.stat(path).st_size == 0:
                await ctx.send('Error file is empty')
            else:
                await ctx.send(file=File(path))
        elif action == 'flush':
            os.system("/usr/local/bin/flush")
            await utils.emoji(ctx, '✅')
        elif action == 'delete':
            os.system("/usr/local/bin/del_bkup")
            await utils.emoji(ctx, '✅')

def setup(client):
    client.add_cog(DeveloperTools(client))
