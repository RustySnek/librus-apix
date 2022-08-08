from bs4 import BeautifulSoup
from librus_apix.get_token import get_token, Token
from librus_apix.urls import BASE_URL, MESSAGE_URL
from librus_apix.exceptions import TokenError, ParseError
from librus_apix.helpers import no_access_check
from dataclasses import dataclass


@dataclass
class Message:
    author: str
    title: str
    date: str
    href: str


def message_content(token: Token, content_url: str) -> str:
    soup = no_access_check(
        BeautifulSoup(token.get(MESSAGE_URL + content_url).text, "lxml")
    )
    content = soup.find("div", attrs={"class": "container-message-content"})
    if content is None:
        raise ParseError("Error in parsing message content.")
    return str(content.text)


def parse(message_soup: BeautifulSoup) -> list[Message]:
    msgs: list[Message] = []
    soup = message_soup.find("table", attrs={"class": "decorated stretch"})
    if soup is None:
        raise ParseError("Error in parsing messages.")
    tds = soup.find("tbody").find_all("tr", attrs={"class": ["line0", "line1"]})
    if tds[0].text.strip() == "Brak wiadomości":
        return []
    for td in tds:
        _tick, _attachment, author, title, date, _trash = td.find_all("td")
        href = author.find("a").attrs["href"].split("/")[4]
        author = str(author.text)
        title = str(title.text)
        date = str(date.text)
        m = Message(author, title, date, href)
        msgs.append(m)
    return msgs


def get_recieved(token: Token, page: int) -> list[Message]:
    payload = {
        "numer_strony105": page,
        "porcjowanie_pojemnik105": 105,
    }
    response = token.post(BASE_URL + "/wiadomosci", data=payload)
    soup = no_access_check(BeautifulSoup(response.text, "lxml"))
    recieved_msgs = parse(soup)
    return recieved_msgs
