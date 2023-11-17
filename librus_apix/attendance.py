from bs4 import BeautifulSoup
from librus_apix.get_token import get_token, Token
from librus_apix.helpers import no_access_check
from librus_apix.urls import BASE_URL, ATTENDANCE_URL
from librus_apix.exceptions import TokenError, ParseError
from typing import Iterable
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Attendance:
    symbol: str
    href: str
    semester: int
    date: str
    type: str
    teacher: str
    period: int
    excursion: bool
    topic: str
    subject: str

def get_detail(token: Token, detail_url: str) -> dict[str, str]:
    details = {}
    div = no_access_check(
        BeautifulSoup(token.get(ATTENDANCE_URL + detail_url).text, "lxml")
    ).find("div", attrs={"class": "container-background"})
    line = div.find_all("tr", attrs={"class": ["line0", "line1"]})
    if len(line) < 1:
        raise ParseError("Error in parsing attendance.")
    for l in line:
        if not l.find("th"):
            continue
        details[l.find("th").text] = l.find("td").text
    return details

def get_attendance(token: Token, sort_by: dict[str, str] = {'zmiany_logowanie_wszystkie': ''}) -> list[list[Attendance]]:
    soup = no_access_check(
            BeautifulSoup(token.post(BASE_URL + "/przegladaj_nb/uczen", data=sort_by).text, "lxml")
    )
    table = soup.find("table", attrs={"class": "center big decorated"})
    if table is None:
        raise ParseError("Error parsing attendance.")
    days = table.find_all("tr", attrs={"class": ["line0", "line1"]})
    current = ""
    att = [[], []]
    semester = 2
    for day in days:
        if current == day.attrs["class"]:
            semester = 1
        current = day.attrs["class"]
        date = day.find("td", attrs={"class": None})
        attendance = day.find_all("td", attrs={"class": "center"})
        for attend in attendance:
            at = attend.find_all("a")
            for single in at:
                if not single:
                    continue
                attributes = { i.split(": ")[0].strip():
                    i.split(": ")[1].strip()
                    for i in single.attrs["title"]
                    .replace("</b>", "<br>")
                    .replace("<br/>", "")
                    .strip()
                    .split("<br>")
                    }
                date = attributes["Data"].split(" ")[0]
                _type = attributes["Rodzaj"]
                school_subject = attributes["Lekcja"]
                topic = attributes["Temat zajęć"]
                period = int(attributes["Godzina lekcyjna"])
                excursion = True if attributes["Czy wycieczka"] == "Tak" else False
                teacher = attributes["Nauczyciel"]

                href = (
                    single.attrs["onclick"]
                    .replace("otworz_w_nowym_oknie(", "")
                    .split(",")[0]
                    .replace("'", "")
                    .split("/")[3]
                )
                a = Attendance(
                    single.text,
                    href,
                    semester,
                    date,
                    _type,
                    teacher,
                    period,
                    excursion,
                    topic,
                    school_subject,
                )
                att[semester-1].append(a)
    return att
