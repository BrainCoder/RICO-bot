import discord
from discord.ext import commands
import settings
intents = discord.Intents.all()
intents.members = True 
client=commands.Bot(command_prefix='!', intients=intents)

class BookClub(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @commands.command(pass_context=True)
    @commands.has_any_role('Book Club Facilitators', 'owners', 'Developer')
    async def bookclub_members(self, ctx):
        guild = ctx.guild
        role = guild.get_role(settings.config["otherRoles"]["book-club"])
        partcipants = [m for m in guild.members if role in m.roles]
        no = len(partcipants)
        print(f'{no}')
        await ctx.send(f'Bookclub members: {no}')


def setup(client):
    client.add_cog(BookClub(client))
