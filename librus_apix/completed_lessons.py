"""
This module provides functions for managing completed lessons from the Librus site, including retrieval, parsing, and pagination.

Classes:
    - Lesson: Represents a completed lesson with attributes such as subject, teacher, topic, etc.

Functions:
    - get_max_page_number: Retrieves the maximum page number for completed lessons within a specified date range.
    - get_completed: Retrieves completed lessons within a specified date range and page number.

Usage:
```python
from librus_apix.client import new_client

# Create a new client instance
client = new_client()
client.get_token(username, password)

# Retrieve the maximum page number for completed lessons within a date range
date_from = "YYYY-MM-DD"
date_to = "YYYY-MM-DD"
max_page_number = get_max_page_number(client, date_from, date_to)

# Retrieve completed lessons within a specified date range and page number
page_number = 0  # Specify the page number
completed_lessons = get_completed(client, date_from, date_to, page=page_number)
```
"""

from typing import List
from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag
from librus_apix.client import Client
from librus_apix.helpers import no_access_check
from librus_apix.exceptions import ParseError
import re


@dataclass
class Lesson:
    """
    Represents a lesson.

    Attributes:
        subject (str): The subject of the lesson.
        teacher (str): The teacher teaching the lesson.
        topic (str): The topic or content of the lesson.
        z_value (str): The z in librus. No clue what it stands for.
        attendance_symbol (str): The symbol representing attendance for the lesson.
        attendance_href (str): The URL associated with the attendance record for the lesson.
        lesson_number (int): The number of the lesson.
        weekday (str): The weekday on which the lesson occurs.
        date (str): The date of the lesson.
    """

    subject: str
    teacher: str
    topic: str
    z_value: str
    attendance_symbol: str
    attendance_href: str
    lesson_number: int
    weekday: str
    date: str


def get_max_page_number(client: Client, date_from: str, date_to: str) -> int:
    """
    Retrieves the maximum page number for completed lessons within a specified date range.

    Args:
        client (Client): The client object used to fetch completed lesson data.
        date_from (str): The start date of the date range (in format "YYYY-MM-DD").
        date_to (str): The end date of the date range (in format "YYYY-MM-DD").

    Returns:
        int: The maximum page number for the completed lessons within the specified date range.

    Raises:
        ParseError: If there is an error while trying to retrieve the maximum page number.
    """
    data = {
        "data1": date_from,
        "data2": date_to,
        "filtruj_id_przedmiotu": -1,
        "numer_strony1001": 0,
        "porcjowanie_pojemnik1001": 1001,
    }
    soup = no_access_check(
        BeautifulSoup(client.post(client.COMPLETED_LESSONS_URL, data=data).text, "lxml")
    )
    try:
        pages = soup.select_one("div.pagination > span")
        if not pages:
            return 0
        max_pages = pages.text.replace("\xa0", "")
        try:
            max_pages_number_re = re.search("z[0-9]*", max_pages)
            if max_pages_number_re is None:
                return 0
            max_pages_number = int(max_pages_number_re.group(0).replace("z", ""))
        except:
            max_pages_number = 0
    except:
        raise ParseError("Error while trying to get max page number.")
    return max_pages_number


def _sanitize_onclick(onclick: str) -> str:
    href = (
        onclick.replace("otworz_w_nowym_oknie(", "")
        .split(",")[0]
        .replace("'", "")
        .split("/")
    )
    if len(href) < 4:
        return ""
    return href[3]


def _create_lesson(line: Tag):
    """
    Creates a Lesson object from a BeautifulSoup Tag representing a completed lesson.

    Args:
        line (Tag): The BeautifulSoup Tag representing a completed lesson.

    Returns:
        Lesson: A Lesson object representing the completed lesson.

    Raises:
        ParseError: If there is an error while parsing the completed lesson data.
    """
    date = line.select_one('td[class="center small"]')
    date = date.text if date is not None else "01-01-2000"
    weekday = line.select_one("td.tiny")
    weekday = weekday.text if weekday is not None else ""
    data = [td.text.strip() for td in line.find_all("td", attrs={"class": None})]
    if len(data) < 5:
        raise ParseError(
            "Error while parsing Completed lesson's data. (data isn't 5 element long)"
        )
    lesson_number, subject_and_teacher, topic, z_value, attendance = data[:5]
    subject_and_teacher = subject_and_teacher.split(", ")
    if len(subject_and_teacher) != 2:
        subject, teacher = (subject_and_teacher[0], subject_and_teacher[0])
    else:
        subject, teacher = subject_and_teacher
    attendance_href = line.select_one("td > p.box > a")
    if attendance_href is not None:
        onclick = attendance_href.attrs.get("onclick", "")
        attendance_href = _sanitize_onclick(onclick)
    else:
        attendance_href = ""

    return Lesson(
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


def get_completed(
    client: Client, date_from: str, date_to: str, page: int = 0
) -> List[Lesson]:
    """
    Retrieves completed lessons within a specified date range and page number.

    Args:
        client (Client): The client object used to fetch completed lesson data.
        date_from (str): The start date of the date range (in format "YYYY-MM-DD").
        date_to (str): The end date of the date range (in format "YYYY-MM-DD").
        page (int, optional): The page number of the completed lessons to retrieve.
            Defaults to 0.

    Returns:
        List[Lesson]: A list of Lesson objects representing the completed lessons.

    Notes:
        - The date_from and date_to parameters do not have a limit on how far apart they can be.
        - If date_from or date_to is empty, it returns completed lessons from the past week.
        - Each page contains 15 lessons. The maximum number of pages can be retrieved using the get_max_page_number() function.
        - If the specified page number exceeds the maximum, it defaults to the maximum available page.

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
        BeautifulSoup(client.post(client.COMPLETED_LESSONS_URL, data=data).text, "lxml")
    )

    lines = soup.select('table[class="decorated"] > tbody > tr')
    completed_lessons = list(map(_create_lesson, lines))
    return completed_lessons
