import random

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


    async def random_user(self, ctx):
        commands.context
        discord.Member.voice
        ctx.author

def main():
    import requests
    for http_code in VALID_HTTP_CODES:
        response = requests.get(f"https://http.cat/{http_code}.jpg")

        if response.status_code == 200:
            continue

        print(http_code.value)


if __name__ == "__main__":
    main()
