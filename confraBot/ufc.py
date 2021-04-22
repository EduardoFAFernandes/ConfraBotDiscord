import requests
from bs4 import BeautifulSoup

from discord.ext import commands


class UFC(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


def main():
    content = requests.get("https://www.ufc.com/events").content
    soup = BeautifulSoup(content, 'html.parser')
    cards = soup.find(class_="l-listing__item")
    print(cards)

if __name__ == "__main__":
    main()
