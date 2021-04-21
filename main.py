import discord
import os

BOT_PROMPT = "$"

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(f'{BOT_PROMPT}hello'):
        await message.channel.send('Hello!')


if __name__ == "__main__":
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    client.run(DISCORD_TOKEN)