from typing import List
from dataclasses import dataclass
from bs4 import BeautifulSoup
from librus_apix.urls import COMPLETED_LESSONS_URL
from librus_apix.get_token import Token
from librus_apix.helpers import no_access_check
from librus_apix.exceptions import ParseError
import re


@dataclass
class Lesson:
    subject: str
    teacher: str
    topic: str
    z_value: str
    attendance_symbol: str
    attendance_href: str
    lesson_number: int
    weekday: str
    date: str


def get_max_page_number(token: Token, date_from, date_to) -> int:
    data = {
        "data1": date_from,
        "data2": date_to,
        "filtruj_id_przedmiotu": -1,
        "numer_strony1001": 0,
        "porcjowanie_pojemnik1001": 1001,
    }
    soup = no_access_check(
        BeautifulSoup(token.post(COMPLETED_LESSONS_URL, data=data).text, "lxml")
    )
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
    return max_pages_number


def get_completed(
    token: Token, date_from: str, date_to: str, page: int = 0
) -> List[Lesson]:
    """
    date_from and date_to don't have a limit of how far apart they can be.
    date_from and date_to can also excceed the current date and will just return an empty list.
    If date_from or date_to is empty it should return the past week. (not exactly sure atm.)

    Each page contains 15 lessons. The maximum amount of pages can be retrieved by using get_max_page_number() function.
    If page exceeds the max amount it will just default to max amount.
    """
    data = {
        "data1": date_from,
        "data2": date_to,
        "filtruj_id_przedmiotu": -1,
        "numer_strony1001": page,
        "porcjowanie_pojemnik1001": 1001,
    }
    completed_lessons = []
    soup = no_access_check(
        BeautifulSoup(token.post(COMPLETED_LESSONS_URL, data=data).text, "lxml")
    )

    lines = soup.select('table[class="decorated"] > tbody > tr')
    for line in lines:
        date = line.select_one('td[class="center small"]').text
        weekday = line.select_one("td.tiny").text
        lesson_number, subject_and_teacher, topic, z_value, attendance = [
            td.text.strip() for td in line.find_all("td", attrs={"class": None})
        ]
        subject, teacher = subject_and_teacher.split(", ")
        attendance_href = ""
        if attendance != "":
            attendance_href = line.select_one("td > p.box > a").text
        lesson = Lesson(
            subject,
            teacher,
            topic,
            z_value,
            attendance,
            attendance_href,
            lesson_number,
            weekday,
            date,
        )
        completed_lessons.append(lesson)
    return completed_lessons
