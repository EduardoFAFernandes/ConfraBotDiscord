import datetime
from functools import lru_cache

import requests
from bs4 import BeautifulSoup

import discord
from discord.ext import commands


class UFC(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ufc_card(self, ctx):

        event_details = get_event_details(get_latest_event_url())

        embed = discord.Embed(title=event_details["name"],
                              url=event_details["url"],
                              description=datetime.datetime.fromtimestamp(int(event_details["timestamp"]))
                                          .strftime("%A %d %B %H:%M"),
                              color=0xdedede)

        embed.set_image(url=event_details["image"])

        for fight in event_details["main_card_fights"]:
            red_fighter_description = f"{fight['red_fighter']['rank']} " \
                                      f"{fight['red_fighter']['first_name']} " \
                                      f"{fight['red_fighter']['last_name']}"
            blue_fighter_description = f"{fight['blue_fighter']['rank']} " \
                                       f"{fight['blue_fighter']['first_name']} " \
                                       f"{fight['blue_fighter']['last_name']}"
            fight_description = f"{red_fighter_description} vs. {blue_fighter_description}"
            embed.add_field(name=fight_description,
                            value=fight["fight_class"],
                            inline=False)
        await ctx.send(embed=embed)


def get_latest_event_url():
    ufc_url = "https://www.ufc.com"
    ufc_events_url = ufc_url + "/events"
    events_content = requests.get(ufc_events_url, **ufc_request_details()).content
    card_path = BeautifulSoup(events_content, 'html.parser') \
        .find(class_="c-card-event--result__logo") \
        .find("a")["href"]
    card_url = ufc_url + card_path
    return card_url


"""
# calling the function without cashing
# duration of 40 call: 15.1532s
# duration per call  :  0.3788s
#
# calling the function with cashing
# duration of 40 call:  0.3662s
# duration per call  :  0.0091s
"""
@lru_cache(maxsize=2)
def get_event_details(event_url):

    event_content = requests.get(event_url, **ufc_request_details()).content

    event_page = BeautifulSoup(event_content, 'html.parser')
    result = dict(
        url=event_url,
        name=event_page.select_one(".field--name-node-title > h1").contents[0].strip(),
        image=event_page.find(class_="c-hero__image")["src"].split("?")[0],
        timestamp=event_page.find(class_="c-event-fight-card-broadcaster__time")["data-timestamp"],
        main_card_fights=parse_fights(event_page.find(id="edit-group-main-card")
                                      .find_all(class_="c-listing-fight"))
    )

    return result


def ufc_request_details():
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
    fights = [
        dict(red_fighter=parse_fighter(fight_data.find(class_="c-listing-fight__corner--red")),
             blue_fighter=parse_fighter(fight_data.find(class_="c-listing-fight__corner--blue")),
             fight_class=fight_data.find(class_="c-listing-fight__class").contents[0])
        for fight_data in fights_data
    ]

    return fights


def parse_fighter(fighter):
    try:
        rank = fighter.select_one(".js-listing-fight__corner-rank > span").contents[0]
    except Exception:
        rank = "U"

    return dict(
        first_name=fighter.find(class_="c-listing-fight__corner-given-name").contents[0],
        last_name=fighter.find(class_="c-listing-fight__corner-family-name").contents[0],
        rank=rank,
    )


if __name__ == "__main__":
    """
    Small test to sue the functools lru_cache
    """
    from timeit import default_timer as timer

    start = timer()
    for i in range(40):
        get_event_details("https://www.ufc.com/event/ufc-fight-night-may-01-2021")
    end = timer()
    duration = end - start
    print(f"duration of 40 call: {duration:2.4f}s\n"
          f"duration per call  : {duration/40:2.4f}s")


