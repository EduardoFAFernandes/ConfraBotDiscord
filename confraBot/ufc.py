import requests
from bs4 import BeautifulSoup

from discord.ext import commands


class UFC(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

def get_latest_event_url():
    ufc_url = "https://www.ufc.com"
    ufc_events_url = ufc_url + "/events"
    events_content = requests.get(ufc_events_url, **ufc_request_details()).content
    card_path = BeautifulSoup(events_content, 'html.parser') \
        .find(class_="c-card-event--result__logo") \
        .find("a")["href"]
    card_url = ufc_url + card_path
    return card_url



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

if __name__ == "__main__":
    pass
