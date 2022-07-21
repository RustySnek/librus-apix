from bs4 import BeautifulSoup
from librus_apix.get_token import get_token, Token
from librus_apix.urls import BASE_URL, MESSAGE_URL
from dataclasses import dataclass

@dataclass
class Message:
    author: str
    title: str
    date: str
    message_href: str

def message_content(token: Token, content_url: str) -> str:
        soup = BeautifulSoup(token.get(MESSAGE_URL + content_url).text, "lxml")
        content = soup.find("div", attrs={"class": "container-message-content"})
        if not content:
            raise Exception("Failed to get message content.")
        return str(content.text)

def parse(message_soup: BeautifulSoup):
    msgs: dict[str, list[Message]] = {'messages': []}
    soup = message_soup.find("table", attrs={"class": "decorated stretch"})
    if soup is None:
        return {'error': 'Malformed token'}, 401
    tds = soup.find("tbody").find_all("tr", attrs={"class": ["line0", "line1"]})
    
    for td in tds:
        _tick, _attachment, author, title, date, _trash = td.find_all("td")
        href = author.find("a").attrs["href"]
        author = str(author.text)
        title = str(title.text)
        date = str(date.text)
        m = Message(author, title, date, href)
        msgs['messages'].append(m.__dict__)
    return msgs, 200


def get_recieved(token: Token, page: int) -> list[Message]:
    payload = {
        "numer_strony105": page,
        "porcjowanie_pojemnik105": 105,}
    response = token.post(BASE_URL + "/wiadomosci", data=payload)
    soup = BeautifulSoup(response.text, "lxml")
    recieved_msgs, status = parse(soup)
    return recieved_msgs, status

