# ConfraBotDiscord
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/EduardoFAFernandes/ConfraBotDiscord/graphs/commit-activity)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)


This is a small bot for a private discord server.
The main codebase is written in Python, and the bot is currently hosted in
[Heroku](https://heroku.com) with auto deployment from the main branch. To interact
with discord [discord.py](https://github.com/Rapptz/discord.py) is used, you can access 
its documentation at [discordpy.readthedocs.io](https://discordpy.readthedocs.io/).

## How to install and run

- Create your bot at the [Discord Developer Portal](https://discord.com/developers/) and get the bot token 
- Add the token as an environment variable :
    - Linux `export DISCORD_TOKEN=your-token-here`
    - Windows ¯\\\_(ツ)_/¯ (good luck...)
- Install [python3](https://www.python.org/downloads/)
- Clone this github project `git clone https://github.com/EduardoFAFernandes/ConfraBotDiscord.git` or just download the zip and extract it
- Install dependencies with the following command: `pip install -r requirements.txt`
- Start the bot using `python main.py`

## How to add commands

The bot is using the Cog extension from the discord package to group similar 
commands if you have just a random command you can use the utils.py cog.

See this [Cog tutorial](https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html#ext-commands-cogs) in the documentation on how to add commands

When you finish your cog you will need to register it in the main file.

```python
bot_cogs = [
    greetings.Greetings,
    utils.Utils
    #add your cog here
]
```

