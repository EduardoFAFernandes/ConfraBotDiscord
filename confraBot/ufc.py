from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

import aiohttp
from bs4 import BeautifulSoup

import discord
from discord.ext import commands
from confraBot.utils import embed_pages


class UFC(commands.Cog):
    """
    This is the UFC Cog that handles all commands related with ufc
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ufc_card(self, ctx: commands.Context):
        """
        A command that sends an embeded view of the next ufc event

        Example in a discord chat:

        Alice> $ufc_card
        Bot> [embeded view of the next ufc Event]
        """

        async with aiohttp.ClientSession(**ufc_request_details()) as session:
            latest_event_url = await get_latest_event_url(session)
            event_details = await get_event_details(latest_event_url, session)

        await embed_pages(self.bot, ctx,
                          pages=[gen_card_embed(event_details, card_type)
                                 for card_type in Cards
                                 if card_type.get_card(event_details) is not None
                                 ])


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
class FightCard:
    """Class to store data fom a fight card"""
    timestamp: int
    card_fights: List[Fight]


@dataclass
class Event:
    """Class to store data fom a UFC Event"""
    url: str
    name: str
    image: str
    main_card: FightCard
    prelims_card: FightCard
    prelims_early_card: FightCard


class Cards(Enum):
    MAIN_CARD = (1, "Main Card", "main_card")
    PRELIMS = (2, "Prelims", "prelims_card")
    EARLY_PRELIMS = (3, "Early Prelims", "prelims_early_card")

    def __init__(self, num, name_str, attr_name):
        self.num = num
        self.name_str = name_str
        self.attr_name = attr_name

    def __str__(self):
        return self.name_str

    def get_card(self, event):
        return event.__getattribute__(self.attr_name)


def gen_card_embed(event_details, card_type):
    card = card_type.get_card(event_details)

    embed = discord.Embed(title=f"{event_details.name} - {card_type}",
                          url=event_details.url,
                          description=f"<t:{card.timestamp}:F>\n<t:{card.timestamp}:R>",
                          color=0xdedede)

    embed.set_image(url=event_details.image)
    embed.set_thumbnail(url="http://pngimg.com/uploads/ufc/ufc_PNG61.png")

    current_page = card_type.num
    total_pages = 2 if event_details.prelims_early_card is None else 3
    embed.set_footer(text=f"{current_page}/{total_pages}")

    for fight in card.card_fights:
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

    return embed


async def get_latest_event_url(session: aiohttp.ClientSession) -> str:
    """
    Fetches the next ufc event url from the events page

    :param session: an aiohttp session where the data request will be made
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


async def get_event_details(event_url: str, session: aiohttp.ClientSession) -> Event:
    """
    Fetches the event page in the event_url and parses the details of the event the result is an Event object.

    :param event_url: The url of a ufc event. Should be somethign like "http://www.ufc.com/events/:event_id"
    :param session: An aiohttp session where the data request will be made
    :return: Event object with the associated event information
    """
    async with session.get(event_url, **ufc_request_details()) as response:
        event_content = await response.text()

    event_page = BeautifulSoup(event_content, 'html.parser')

    return Event(
        url=event_url,
        name=event_page.select_one(".field--name-node-title > h1").contents[0].strip(),
        image=event_page.find(class_="c-hero__image")["src"].split("?")[0],
        main_card=parse_card(event_page.find(class_="main-card")),
        prelims_card=parse_card(event_page.find(class_="fight-card-prelims")),
        prelims_early_card=parse_card(event_page.find(class_="fight-card-prelims-early"))

    )


def ufc_request_details() -> Dict[str, Dict[str, str]]:
    """
    Default cookies and headers to get a response from the ufc website
    The included cookies make the data appear in english.
    The header information just makes it look like a normal browser making a request.

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


def parse_card(card_page: BeautifulSoup) -> FightCard:
    timestamp_elem = card_page.find(class_="c-event-fight-card-broadcaster__time")

    if timestamp_elem is None:
        return None

    return FightCard(
        timestamp=int(timestamp_elem["data-timestamp"]),
        card_fights=parse_fights(card_page.find_all(class_="c-listing-fight"))
    )


def parse_fights(fights_data: BeautifulSoup) -> List[Fight]:
    """
    Extracts information from a list of ufc fights from a given event card

    :param fights_data: A BeautifulSoup object with multiple fights inside.
    :return: A list of fights contained in the fights_data
    """
    fights = [
        Fight(red_fighter=parse_fighter(fight_data.find(class_="c-listing-fight__corner--red")),
              blue_fighter=parse_fighter(fight_data.find(class_="c-listing-fight__corner--blue")),
              fight_class=fight_data.find(class_="c-listing-fight__class").contents[0])
        for fight_data in fights_data
    ]

    return fights


def parse_fighter(fighter: BeautifulSoup) -> Fighter:
    """
    Extracts information of a figter in a given fight

    :param fighter: fighter data
    :return: A Fighter contained in the figter param
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
