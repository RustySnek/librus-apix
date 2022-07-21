from bs4 import BeautifulSoup
from get_token import get_token, Token
from urls import BASE_URL, ATTENDANCE_URL
from typing import Iterable
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class Attendance:
    symbol: str
    href: str
    _type: str
    date: str
    lesson: str
    subject: str
    teacher: str
    hour: str
    excursion: str
    by: str
    semester: int

def get_detail(token: Token, detail_url: str) -> dict[str, str]:
    details = {}
    line = (
        BeautifulSoup(token.get(ATTENDANCE_URL + detail_url).text, "lxml")
        .find("div", attrs={"class": "container-background"})
        .find_all("tr", attrs={"class": ["line0", "line1"]})
    )
    if line is None:
        return {'error': 'Malformed token'}, 401
    for l in line:
        if not l.find("th"):
            continue
        details[l.find("th").text] = l.find("td").text
    return details, 200

def get_attendance(token: Token) -> Iterable[Attendance]:
    soup = BeautifulSoup(token.get(BASE_URL + "/przegladaj_nb/uczen").text, "lxml")
    days = soup.find("table", attrs={"class": "center big decorated"}).find_all(
        "tr", attrs={"class": ["line0", "line1"]}
    )
    if days is None:
        return {'error': 'Malformed token'}, 401
    current = ""
    att = defaultdict(list)
    semester = 1
    for day in days:
        if current == day.attrs['class']:
            semester = 2
        current = day.attrs['class']
        date = day.find("td", attrs={"class": None})
        attendance = day.find_all("td", attrs={"class": "center"})
        for attend in attendance:
            at = attend.find_all("a")
            for single in at:
                if not single:
                    continue
                _type, date, lesson, subject, teacher, hour, excursion, by = (
                    i.split(": ")[1].strip()
                    for i in single.attrs["title"]
                    .replace("</b>", "<br>")
                    .replace("<br/>", "")
                    .strip()
                    .split("<br>")
                )
                href = (
                    single.attrs["onclick"]
                    .replace("otworz_w_nowym_oknie(", "")
                    .split(",")[0]
                    .replace("'", "")
                    .split('/')[3]
                )
                a = Attendance(
                    single.text,
                    href,
                    _type,
                    date.split(" ")[0],
                    lesson,
                    subject,
                    teacher,
                    hour,
                    excursion,
                    by,
                    semester,
                )
                att[semester].append(a.__dict__)
    return att, 200