from typing import Optional

from discord import Embed
from discord.ext import commands
from discord.utils import get
from discord.ext.menus import MenuPages, ListPageSource


def syntax(command):
    cmd_and_aliases = "|".join([str(command), *command.aliases])
    params = []

    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")
    params = " ".join(params)
    return f"```{cmd_and_aliases} {params}```"


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=3)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(title="Help", description="Welcome to the NPC help dialog!", colour=self.ctx.author.colour)
        embed.set_thumbnail(url=self.ctx.guild.icon_url)
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} of {len_data:,} commands.")

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
        return embed

    async def format_page(self, menu, entries):
        fields = []
        for entry in entries:
            fields.append((entry.name or "No description", syntax(entry)))
        return await self.write_page(menu, fields)


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.remove_command('help')

    async def cmd_help(self, ctx, command):
        embed = Embed(title=f'Help with `{command}`', description=syntax(command), colour=ctx.author.colour)
        embed.add_field(name='Command description', value=command.help)
        await ctx.send(embed=embed)

    @commands.command(name="help", aliases=['h'])
    async def show_help(self, ctx, cmd: Optional[str]):
        """Im not explaining this, if you do not know what this command does then I cannot help you"""
        if cmd is None:
            await ctx.message.delete()
            menu = MenuPages(source=HelpMenu(ctx, list(self.client.commands)),
                    delete_message_after=True,
                    timeout=60.0)
            await menu.start(ctx)
        else:
            command = get(self.client.commands, name=cmd)
            if command:
                await self.cmd_help(ctx, command)
            else:
                await ctx.send('That command does not exist.')


def setup(client):
    client.add_cog(Help(client))
