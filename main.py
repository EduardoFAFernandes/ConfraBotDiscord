import discord
import os
import random

from discord.ext import commands

# importing cogs
from confraBot import greetings, utils, ufc

BOT_PROMPT = "$"

bot = commands.Bot(command_prefix=BOT_PROMPT)
bot_cogs = [
    greetings.Greetings,
    utils.Utils,
    ufc.UFC
]

for cog in bot_cogs:
    bot.add_cog(cog(bot))


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


if __name__ == "__main__":
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(DISCORD_TOKEN)