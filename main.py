import discord
import os

from discord.ext import commands

from confraBot import greetings, utils, ufc
import bot_config 

def main():
    BOT_PROMPT = get_config_param("BOT_PROMPT")
    DISCORD_TOKEN = get_config_param("DISCORD_TOKEN")

    bot = commands.Bot(command_prefix=BOT_PROMPT)
    bot_cogs = [
        greetings.Greetings,
        utils.Utils,
        ufc.UFC
        # add your cog here
    ]

    for cog in bot_cogs:
        bot.add_cog(cog(bot))


    @bot.event
    async def on_ready():
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')

    
    bot.run(DISCORD_TOKEN)


def get_config_param(param_name:str):
    default_param = None
    file_param = bot_config.CONFIG.get(param_name, default_param)
    environment_param = os.getenv(param_name, file_param)
    return environment_param


if __name__ == "__main__":
    main()
