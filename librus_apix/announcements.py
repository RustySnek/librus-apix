from typing import List
from bs4 import BeautifulSoup
from librus_apix.get_token import Token
from librus_apix.helpers import no_access_check
from dataclasses import dataclass
from librus_apix.exceptions import ParseError


@dataclass
class Announcement:
    title: str = ""
    author: str = ""
    description: str = ""
    date: str = ""


def get_announcements(token: Token) -> List[Announcement]:
    soup = no_access_check(
        BeautifulSoup(token.get(token.ANNOUNCEMENTS_URL).text, "lxml")
    )
    announcements = []
    announcement_tables = soup.select("table.decorated.big.center.printable.margin-top")
    if len(announcement_tables) < 1:
        raise ParseError("Error in parsing announcements")
    for table in announcement_tables:
        title = table.select_one("thead > tr > td").text
        author, date, desc = [
            line.select_one("td").text.strip()
            for line in table.find_all("tr", attrs={"class": ["line0", "line1"]})
        ]
        a = Announcement(title, author, desc, date)
        announcements.append(a)
    return announcements
