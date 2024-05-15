from typing import List
from bs4 import BeautifulSoup
from librus_apix.get_token import Token
from librus_apix.exceptions import ParseError
from librus_apix.helpers import no_access_check
from dataclasses import dataclass
import re


@dataclass
class MessageData:
    author: str
    title: str
    content: str
    date: str


@dataclass
class Message:
    author: str
    title: str
    date: str
    href: str
    unread: bool
    has_attachment: bool


def recipient_groups(token) -> List[str]:
    soup = no_access_check(
        BeautifulSoup(token.get(token.RECIPIENT_GROUPS_URL).text, "lxml")
    )
    groups = []
    trs = soup.select("table.message-recipients > tbody > tr")
    for tr in trs:
        radio = tr.select_one("input.recipiantTypeRadio")
        if radio is None:
            raise ParseError("Error getting groups (radio)")
        groups.append(radio.attrs.get("value", ""))
    return groups


def get_recipients(token: Token, group: str):
    payload = {
        "typAdresata": group,
        "poprzednia": 5,
        "tabZaznaczonych": "",
        "czyWirtualneKlasy": False,
        "idGrupy": 0,
    }
    soup = no_access_check(
        BeautifulSoup(token.post(token.RECIPIENTS_URL, data=payload).text, "lxml")
    )
    labels = soup.select("label")
    teachers = {}
    for label in labels:
        teachers[label.text.replace("\xa0", "")] = label.attrs.get("for", "").split(
            "_"
        )[-1]
    return teachers


def send_message(
    token: Token,
    title: str,
    content: str,
    recipient_ids: list[str],
):
    payload = {
        "filtrUzytkownikow": 0,
        "idPojemnika": "",
        "DoKogo": recipient_ids,
        "Rodzaj": 0,
        "temat": title,
        "tresc": content,
        "poprzednia": 5,
        "fileStorageIdentifier": "",
        "wyslij": "Wyślij",
    }
    sent_message = no_access_check(
        BeautifulSoup(token.post(token.SEND_MESSAGE_URL, data=payload).text, "lxml")
    )
    result = sent_message.select_one("div.container-background > p")
    if result is None:
        raise ParseError("Error getting the result of the message!")
    result = result.text
    if "nie zostala" in result.text:
        return {False, result}
    if sent_message.status_code == 200:
        return {True, result}
    return {False, result}


def unwrap_message_data(tr):
    value = tr.select_one("td[class='left']")
    return value.text if value is not None else ""


def message_content(token: Token, content_url: str) -> MessageData:
    soup = no_access_check(
        BeautifulSoup(token.get(token.MESSAGE_URL + "/" + content_url).text, "lxml")
    )
    message_data = soup.select_one("table[class='stretch']")
    if message_data is None:
        raise ParseError("Error in parsing message data.")
    trs = message_data.select("tr")
    if len(trs) < 3:
        raise ParseError("Not enough values to unpack from message_data")
    author, title, date = trs[:3]
    content = soup.find("div", attrs={"class": "container-message-content"})
    if content is None:
        raise ParseError("Error in parsing message content.")
    return MessageData(
        unwrap_message_data(author),
        unwrap_message_data(title),
        content.text,
        unwrap_message_data(date),
    )


def parse_sent(message_soup: BeautifulSoup) -> List[Message]:
    msgs: List[Message] = []
    hasAttachment = False
    soup = message_soup.find("table", attrs={"class": "decorated stretch"})
    if soup is None:
        raise ParseError("Error in parsing messages.")
    tbody = soup.find("tbody")
    if tbody is None:
        raise ParseError("Error in parsing messages (tbody).")
    tds = tbody.find_all("tr", attrs={"class": ["line0", "line1"]})
    if tds[0].text.strip() == "Brak wiadomości":
        return []
    for td in tds:
        hasAttachment = False
        _tick, attachment, author, title, date, unread, _trash = td.find_all("td")
        if attachment.find("img"):
            hasAttachment = True
        unread = True if unread == "NIE" else False
        href = author.find("a")
        href = href.attrs["href"].split("/")[4] if href is not None else ""
        author = str(author.text)
        title = str(title.text)
        date = str(date.text)
        m = Message(author, title, date, href, unread, hasAttachment)
        msgs.append(m)
    return msgs


def parse(message_soup: BeautifulSoup) -> List[Message]:
    msgs: List[Message] = []
    hasAttachment = False
    soup = message_soup.find("table", attrs={"class": "decorated stretch"})
    if soup is None:
        raise ParseError("Error in parsing messages.")
    tbody = soup.find("tbody")
    if tbody is None:
        raise ParseError("Error in parsing messages (tbody).")
    tds = tbody.find_all("tr", attrs={"class": ["line0", "line1"]})
    if tds[0].text.strip() == "Brak wiadomości":
        return []
    for td in tds:
        unread = False
        hasAttachment = False
        _tick, attachment, author, title, date, _trash = td.find_all("td")
        if attachment.find("img"):
            hasAttachment = True
        if title.get("style") and "font-weight: bold" in title.get("style"):
            unread = True

        href = author.find("a")
        href = href.attrs["href"].split("/")[4] if href is not None else ""
        author = str(author.text)
        title = str(title.text)
        date = str(date.text)
        m = Message(author, title, date, href, unread, hasAttachment)
        msgs.append(m)
    return msgs


def get_max_page_number(token: Token) -> int:
    soup = no_access_check(BeautifulSoup(token.get(token.MESSAGE_URL).text, "lxml"))
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
    response = token.post(token.MESSAGE_URL, data=payload)
    soup = no_access_check(BeautifulSoup(response.text, "lxml"))
    recieved_msgs = parse(soup)
    return recieved_msgs


def get_sent(token: Token, page: int) -> List[Message]:
    payload = {
        "numer_strony105": page,
        "porcjowanie_pojemnik105": 105,
    }
    response = token.post(token.SEND_MESSAGE_URL, data=payload)
    soup = no_access_check(BeautifulSoup(response.text, "lxml"))
    recieved_msgs = parse_sent(soup)
    return recieved_msgs
