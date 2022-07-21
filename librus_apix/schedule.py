from bs4 import BeautifulSoup
from get_token import Token, get_token
from urls import BASE_URL, SCHEDULE_URL
from dataclasses import dataclass

@dataclass
class Day:
    title: str
    day: str
    href: str = ""    

def schedule_detail(token: Token, prefix: str, detail_url: str) -> dict[str, str]:
    schedule = {}
    tr = (
    BeautifulSoup(token.get(SCHEDULE_URL + prefix + "/" + detail_url).text, "lxml")
    .find("div", attrs={"class": "container-background"})
    .find_all("tr", attrs={"class": ["line0", "line1"]})
    )
    if tr is None:
        return {'error': 'Malformed token'}
    for s in tr:
        schedule[s.find("th").text.strip()] = s.find("td").text.strip()

    return schedule, 200


def get_schedule(token: Token, month: str, year: str) -> list[Day]:
    schedule = {'schedule': []}
    soup = BeautifulSoup(
        token.post(BASE_URL + "/terminarz", data={"rok": year, "miesiac": month}).text,
        "lxml",
    )
    days = soup.find_all("div", attrs={"class": "kalendarz-dzien"})
    if len(days) < 1:
        return {'error': 'Malformed token'}, 401
    for day in days:
        d = day.find("div", attrs={"class": "kalendarz-numer-dnia"}).text
        tr = day.find_all("tr")
        if tr:
            for event in tr:
                title = event.find("td").text.strip()
                try:
                    onclick = event.find("td").attrs["onclick"]
                    href = "/".join(onclick.split("'")[1].split('/')[2:])
                    _day = Day(title, d, href)
                    schedule['schedule'].append(_day)
                except KeyError:
                    _day = Day(title, d)
                    schedule['schedule'].append(_day)
        else:
            schedule['schedule'].append(Day("Empty", d))
    return schedule, 200
