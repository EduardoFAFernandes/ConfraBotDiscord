import datetime
from dataclasses import dataclass

import aiohttp
from bs4 import BeautifulSoup

import discord
from discord.ext import commands


class UFC(commands.Cog):
    """
    This is the UFC Cog that handles all commands related with ufc
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ufc_card(self, ctx):
        """
        A command that sends an embeded view of the next ufc event

        Example in a discord chat:

        Alice> $ufc_card
        Bot> [embeded view of the next ufc Event]
        """

        async with aiohttp.ClientSession(**ufc_request_details()) as session:
            latest_event_url = await get_latest_event_url(session)
            event_details = await get_event_details(latest_event_url, session)

        embed = discord.Embed(title=event_details.name,
                              url=event_details.url,
                              description=datetime.datetime.fromtimestamp(event_details.timestamp)
                              .strftime("%A %d %B %H:%M"),
                              color=0xdedede)

        embed.set_image(url=event_details.image)
        embed.set_thumbnail(url="http://pngimg.com/uploads/ufc/ufc_PNG61.png")

        for fight in event_details.main_card_fights:
            red_fighter_description = f"{fight.red_fighter.rank} " \
                                      f"{fight.red_fighter.first_name} " \
                                      f"{fight.red_fighter.last_name}"
            blue_fighter_description = f"{fight.blue_fighter.rank} " \
                                       f"{fight.blue_fighter.first_name} " \
                                       f"{fight.blue_fighter.last_name}"
            fight_description = f"{red_fighter_description} vs. {blue_fighter_description}"
            embed.add_field(name=fight_description,
                            value=fight.fight_class,
                            inline=False)

        await ctx.send(embed=embed)


@dataclass
class Fighter:
    """Class to store data from a fighter."""
    first_name: str
    last_name: str
    rank: str


@dataclass
class Fight:
    """Class to store data from a fight."""
    red_fighter: Fighter
    blue_fighter: Fighter
    fight_class: str


@dataclass
class Event:
    """Class to store data fom a fight"""
    url: str
    name: str
    image: str
    timestamp: int
    main_card_fights: List[Fight]


async def get_latest_event_url(session):
    """
    Fetches the next ufc event url from the events page

    Example:
    >>> import aiohttp
    >>> async with aiohttp.ClientSession() as session:
    ...     latest_event_ur = await get_latest_event_url(session)
    ...
    'https://www.ufc.com/event/ufc-261'

    :return: The url of the next ufc event
    """

    ufc_url = "https://www.ufc.com"
    ufc_events_url = ufc_url + "/events"
    async with session.get(ufc_events_url, **ufc_request_details()) as response:
        events_content = await response.text()

    card_path = BeautifulSoup(events_content, 'html.parser') \
        .find(class_="c-card-event--result__logo") \
        .find("a")["href"]
    card_url = ufc_url + card_path
    return card_url


async def get_event_details(event_url, session):
    """
    Fetches the event page in the event_url and parses the details of the event sutch:
        name, image, timestamp and main card fights

    Example:
    >>> get_event_details("https://www.ufc.com/event/ufc-261")
    {'url': 'https://www.ufc.com/event/ufc-261', 'name': 'UFC 261', 'image': '...', ...}

    :param event_url: The url of an event
    :return: dictionary with event information
    """
    async with session.get(event_url, **ufc_request_details()) as response:
        event_content = await response.text()

    event_page = BeautifulSoup(event_content, 'html.parser')

    return Event(
        url=event_url,
        name=event_page.select_one(".field--name-node-title > h1").contents[0].strip(),
        image=event_page.find(class_="c-hero__image")["src"].split("?")[0],
        timestamp=event_page.find(class_="c-event-fight-card-broadcaster__time")["data-timestamp"],
        main_card_fights=parse_fights(event_page.find(id="edit-group-main-card")
                                      .find_all(class_="c-listing-fight"))
    )



def ufc_request_details():
    """
    Default cookies and headers to get a response from the ufc website

    Example:
    >>> import requests
    >>> requests.get("http://www.ufc.com", **ufc_request_details())
    <Response [200]>

    :return: dictionary with two values: cookies and headers
    """
    cookies = {
        'STYXKEY_region': 'LATIN_AMERICA.PT.en.Default',  # important to get results in english
    }

    headers = {
        'authority': 'www.ufc.com',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '^\\^',
        'sec-ch-ua-mobile': '?0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.ufc.com/events',
        'accept-language': 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    return dict(cookies=cookies, headers=headers)


def parse_fights(fights_data):
    """
    Extracts information from a list of ufc fights from a given event card
    :param fights_data:
    :return:
    """
    fights = [
        Fight(red_fighter=parse_fighter(fight_data.find(class_="c-listing-fight__corner--red")),
              blue_fighter=parse_fighter(fight_data.find(class_="c-listing-fight__corner--blue")),
              fight_class=fight_data.find(class_="c-listing-fight__class").contents[0])
        for fight_data in fights_data
    ]

    return fights


def parse_fighter(fighter):
    """
    Extracts information of a figter in a given fight
    :param fighter: fighter data
    :return:
    """
    try:
        rank = fighter.select_one(".js-listing-fight__corner-rank > span").contents[0]
    except Exception:
        rank = "U"  # Presents U When the fighter is unranked

    return Fighter(first_name=fighter.find(class_="c-listing-fight__corner-given-name").contents[0],
                   last_name=fighter.find(class_="c-listing-fight__corner-family-name").contents[0],
                   rank=rank)


async def main():
    """
    Small test to the module
    """
    from timeit import default_timer as timer

    start = timer()

    async with aiohttp.ClientSession(**ufc_request_details()) as session:
        latest_event_url = await get_latest_event_url(session)
        event_details = await get_event_details(latest_event_url, session)

    end = timer()
    duration = end - start

    print(event_details)
    print(f"duration  : {duration / 40:2.4f}s")


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
