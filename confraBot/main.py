import discord
import os
import random

from discord.ext import commands

from confraBot import greetings

BOT_PROMPT = "$"

bot = commands.Bot(command_prefix=BOT_PROMPT)
bot_cogs = [
    greetings.Greetings]

for cog in bot_cogs:
    bot.add_cog(cog(bot))


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)


if __name__ == "__main__":
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(DISCORD_TOKEN)