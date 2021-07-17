import random

from asyncio import TimeoutError

import discord
from discord.ext import commands

VALID_HTTP_CODES = [100, 101, 102, 200, 201, 202, 204, 206, 207, 300, 301, 302, 303, 304,
                    305, 307, 308, 400, 401, 402, 403, 404, 405, 406, 408, 409, 410, 411,
                    412, 413, 414, 415, 416, 417, 418, 420, 421, 422, 423, 424, 425, 426,
                    429, 431, 444, 450, 451, 499, 500, 501, 502, 503, 504, 506, 507, 508,
                    509, 510, 511, 599]

VALID_HTTP_CODES_SET = set(VALID_HTTP_CODES)


class Utils(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, ctx, dice: str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send('Format has to be in NdN!')
            return

        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await ctx.send(result)

    @commands.command()
    async def http_cat(self, ctx, http_code: int = None):
        """Explains HTTP codes with cat photos"""

        if http_code is None:
            http_code = random.choice(VALID_HTTP_CODES)
        elif http_code not in VALID_HTTP_CODES_SET:
            await ctx.send("Sorry, no photo for that cat.")
            return

        embed = discord.Embed()
        embed.set_image(url=f"https://http.cat/{http_code}.jpg")
        await ctx.send(embed=embed)

    @commands.command()
    async def embedpages_cmd(self, ctx):
        """Example of embed_pages """
        page1 = discord.Embed(
            title='Page 1/3',
            description='Description for page number one.',
            colour=discord.Colour.orange()
        )
        page2 = discord.Embed(
            title='Page 2/3',
            description='Description of the second page.',
            colour=discord.Colour.orange()
        )
        page3 = discord.Embed(
            title='Page 3/3',
            description='Description of the third and final page',
            colour=discord.Colour.orange()
        )

        pages = [page1, page2, page3]
        await embed_pages(self.bot, ctx, pages)


async def embed_pages(bot, ctx, pages, timeout=30.0):
    pages_idx_last = len(pages) - 1

    message = await ctx.send(embed=pages[0])

    controls = {
        '⏮': lambda idx: 0,
        '◀': lambda idx: max(pages_idx - 1, 0),
        '▶': lambda idx: min(pages_idx + 1, pages_idx_last),
        '⏭': lambda idx: pages_idx_last
    }

    for emoji in controls.keys():
        await message.add_reaction(emoji)

    pages_idx = 0

    while True:
        try:
            emoji, user = await bot.wait_for('reaction_add',
                                             timeout=timeout,
                                             check=lambda reaction, user: user == ctx.author and reaction.message == message) # only author can
        except TimeoutError:
            break

        await message.remove_reaction(emoji, user)

        pages_idx = controls.get(str(emoji))(pages_idx)  # updating the pages_idx according to the selected emoji
        await message.edit(embed=pages[pages_idx])

    await message.clear_reactions()
