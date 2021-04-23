import discord
from discord.ext import commands


class Greetings(commands.Cog):
    """
    An Example Cog that sever as a greter

    adapted from: https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html#quick-example
    """

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None


    @commands.command()
    async def hello(self, ctx, *, member: discord.Member = None):
        """
        A command that responds hello to a given user that invoked the command

        Example in a discord chat:

        Alice> $hello
        Bot> $Hello @Alice
        Alice> $hello
        Bot> $Hello @Alice... This feels familiar.

        """
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send(f'Hello {member.name}')
        else:
            await ctx.send(f'Hello {member.name}... This feels familiar.')
        self._last_member = member
