from typing import List
from bs4 import BeautifulSoup
from librus_apix.get_token import Token
from librus_apix.exceptions import ParseError
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


def recipient_groups():
    return {
        "teachers": "nauczyciel",
        "tutors": "wychowawca",
        "parent_council": "szkolna_rada_rodzicow",
        "pedagogue": "pedagog",
        "admin": "admin",
        "secretary": "sekretariat",
    }


def get_recipients(token: Token, group: str = "teachers"):
    groups = recipient_groups()
    if group not in groups:
        raise ValueError(
            f"{group} group is not available. Available groups: {' | '.join(groups.keys())}"
        )
    group = groups[group]
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
    recipient_group: str,
    recipient_ids: list[str],
):
    """
    librus' amazing requests include all possible teacher ids for the group inside the payload.
    The recipients are differentiated by lack of '_hid' in the key.
    It might not be needed but I would rather not send a test message to everyone in school accidentally.
    if anyone is willing to give it a test, good luck.
    """
    all_recipients_ids = list(get_recipients(token, recipient_group).values())
    payload = {
        "filtrUzytkownikow": 0,
        "idPojemnika": "",
        "adresat": recipient_groups().get(recipient_group, ""),
        "DoKogo_hid": list(
            filter(lambda id: id not in recipient_ids, all_recipients_ids)
        ),
        "DoKogo": list(filter(lambda id: id in recipient_ids, all_recipients_ids)),
        "Rodzaj": 0,
        "temat": title,
        "tresc": content,
        "poprzednia": 5,
        "fileStorageIdentifier": "",
        "wyslij": "Wyślij",
    }
    sent_message = token.post(token.SEND_MESSAGE_URL, data=payload)

    if sent_message.status_code == 200:
        return True

    return False


def message_content(token: Token, content_url: str) -> str:
    soup = no_access_check(
        BeautifulSoup(token.get(token.MESSAGE_URL + "/" + content_url).text, "lxml")
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
