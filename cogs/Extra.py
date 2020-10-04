import discord
from discord.ext import commands
from discord.utils import get

client=commands.Bot(command_prefix='!')

class Extra(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_member = None

    @client.command()
    async def DoSomething(self, ctx):
        await ctx.channel.send("*Does your mum*")

    @client.command()
    async def habibi(self, ctx):
        await ctx.message.delete()
        await ctx.send("""
            \
             <:despair:568237870288994315>     Pass the habibi down
            /
         /
    """)
    @client.command()

    @commands.has_role("VIP")
    async def UI(self, ctx, *, member: discord.Member = None):
        DateCreated = member.created_at.strftime("%A, %B %d %Y at %H:%M:%S %p")

        MemberJoinedAt = member.joined_at.strftime("%A, %B %d %Y at %H:%M:%S %p")
        userAvatarUrl = member.avatar_url

        embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)

        embed.set_author(name="UI", icon_url=userAvatarUrl)
        embed.add_field(name='Account was created at: ', value=f"{DateCreated}.")
        embed.add_field(name="Member joined at: ", value=f"{MemberJoinedAt}.")
        embed.add_field(name=f"{member.display_name}'s ", value=f"Avatar is: ")
        await ctx.send(embed=embed)
        await ctx.send(f"{userAvatarUrl}")
        # await ctx.send(f"{ctx.author.name}'s avatar is: {userAvatarUrl}")

    @client.command()
    @commands.has_role("VIP")
    async def avatar(self, ctx, *, avamember: discord.Member = None):
        userAvatarUrl = avamember.avatar_url
        await ctx.send(f"{ctx.author}'s avatar is: {userAvatarUrl}")

def setup(client):
    client.add_cog(Extra(client))
