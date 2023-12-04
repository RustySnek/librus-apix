from typing import List
from bs4 import BeautifulSoup
from librus_apix.get_token import get_token, Token
from librus_apix.urls import BASE_URL, MESSAGE_URL
from librus_apix.exceptions import TokenError, ParseError
from librus_apix.helpers import no_access_check
from dataclasses import dataclass
import re


@dataclass
class Message:
    author: str
    title: str
    date: str
    href: str
    unread: bool
    has_attachment: bool


def message_content(token: Token, content_url: str) -> str:
    soup = no_access_check(
        BeautifulSoup(token.get(MESSAGE_URL + content_url).text, "lxml")
    )
    content = soup.find("div", attrs={"class": "container-message-content"})
    if content is None:
        raise ParseError("Error in parsing message content.")
    return str(content.text)


def parse(message_soup: BeautifulSoup) -> List[Message]:
    msgs: List[Message] = []
    hasAttachment = False
    soup = message_soup.find("table", attrs={"class": "decorated stretch"})
    if soup is None:
        raise ParseError("Error in parsing messages.")
    tds = soup.find("tbody").find_all("tr", attrs={"class": ["line0", "line1"]})
    if tds[0].text.strip() == "Brak wiadomości":
        return []
    for td in tds:
        unread = False
        hasAttachment = False
        _tick, attachment, author, title, date, _trash = td.find_all("td")
        if attachment.find("img") != False:
            hasAttachment = True
        if title.get("style") and "font-weight: bold" in title.get("style"):
            unread = True

        href = author.find("a").attrs["href"].split("/")[4]
        author = str(author.text)
        title = str(title.text)
        date = str(date.text)
        m = Message(author, title, date, href, unread, hasAttachment)
        msgs.append(m)
    return msgs


def get_max_page_number(token: Token) -> int:
    soup = no_access_check(
        BeautifulSoup(token.get(BASE_URL + "/wiadomosci").text, "lxml")
    )
    try:
        pages = soup.select_one("div.pagination > span")
        if not pages:
            return 0
        max_pages = pages.text.replace("\xa0", "")
        max_pages_number = int(
            re.search("z[0-9]*", max_pages).group(0).replace("z", "")
        )
    except:
        raise ParseError("Error while trying to get max page number.")
    return max_pages_number - 1


def get_recieved(token: Token, page: int) -> List[Message]:
    payload = {
        "numer_strony105": page,
        "porcjowanie_pojemnik105": 105,
    }
    response = token.post(BASE_URL + "/wiadomosci", data=payload)
    soup = no_access_check(BeautifulSoup(response.text, "lxml"))
    recieved_msgs = parse(soup)
    return recieved_msgs
