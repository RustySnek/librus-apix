from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from get_token import get_token, Token
from urls import ANNOUNCEMENTS_URL
from dataclasses import dataclass

@dataclass
class Announcement:
    title: str = ""
    author: str = ""
    description: str = ""
    date: str = ""

def get_announcements(token: Token) -> dict[str, dict[str, str]]:
    soup = BeautifulSoup(token.get(ANNOUNCEMENTS_URL).text, "lxml")
    announcements = {'announcements': []}
    announcement_tables = soup.select('table.decorated.big.center.printable.margin-top')
    if len(announcement_tables) < 1:
        return {'error': 'Malformed token'}, 401
    for table in announcement_tables:
        title = table.select_one('thead > tr > td').text
        author, date, desc = [line.select_one('td').text.strip() for line in table.find_all('tr', attrs={'class': ['line0', 'line1']})]
        a = Announcement(title, author, desc, date)
        announcements['announcements'].append(a.__dict__)
    return announcements, 200
