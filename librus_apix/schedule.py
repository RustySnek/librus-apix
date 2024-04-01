from bs4 import BeautifulSoup
from librus_apix.get_token import Token
from librus_apix.exceptions import ParseError
from librus_apix.helpers import no_access_check
from collections import defaultdict
from dataclasses import dataclass
import re
from typing import Union, List, Dict


@dataclass
class Event:
    title: str
    subject: str
    data: dict
    day: str
    number: Union[int, str]
    hour: str
    href: str


def schedule_detail(token: Token, prefix: str, detail_url: str) -> Dict[str, str]:
    schedule = {}
    div = no_access_check(
        BeautifulSoup(
            token.get(token.SCHEDULE_URL + prefix + "/" + detail_url).text, "lxml"
        ).find("div", attrs={"class": "container-background"})
    )
    if div is None:
        raise ParseError("Error in parsing schedule details.")
    tr = div.find_all("tr", attrs={"class": ["line0", "line1"]})
    for s in tr:
        schedule[s.find("th").text.strip()] = s.find("td").text.strip()
    return schedule


def get_schedule(token: Token, month: str, year: str, include_empty: bool = False) -> Dict[int, List[Event]]:
    schedule = defaultdict(list)
    soup = no_access_check(
        BeautifulSoup(
            token.post(token.SCHEDULE_URL, data={"rok": year, "miesiac": month}).text,
            "lxml",
        )
    )
    days = soup.find_all("div", attrs={"class": "kalendarz-dzien"})
    if len(days) < 1:
        raise ParseError("Error in parsing days of the schedule.")
    for day in days:
        d = day.find("div", attrs={"class": "kalendarz-numer-dnia"}).text
        if include_empty == True:
            schedule[int(d)] = []
        tr = day.find_all("tr")
        if tr:
            for event in tr:
                td = event.find("td")
                title = td.attrs.get("title", "Nauczyciel: unknown<br />Opis: unknown")
                additional_data = {key: val for key, val in [pair.split(": ", 1) for pair in title.split("<br />")]}
                subject = "unspecified"
                span = td.find("span")
                if span:
                    subject = span.text
                    span.extract()

                delimeter = "###"
                for line in td.select("br"):
                    line.replaceWith(delimeter)
                data = (
                    td.text.replace("\xa0", " ")
                    .replace(", ", "")
                    .replace("\n", "")
                    .strip()
                    .split(delimeter)
                )
                if len(data) >= 2:
                    title = data[1]
                else:
                    title = data[0]

                number = "unknown"
                hour = "unknown"
                try:
                    number = int(
                        re.findall(r": ?[0-99]?[0-99]", event.find("td").text)[
                            0
                        ].replace(": ", "")
                    )
                except ValueError:
                    hour = re.findall(
                        r" ?[0-2]?[0-9]:?[0-5]?[0-9]", event.find("td").text
                    )[0]
                except IndexError:
                    pass
                try:
                    onclick = event.find("td").attrs["onclick"]
                    href = "/".join(onclick.split("'")[1].split("/")[2:])
                except KeyError:
                    href = ""

                event = Event(title, subject, additional_data, d, number, hour, href)
                schedule[int(d)].append(event)
    return schedule
