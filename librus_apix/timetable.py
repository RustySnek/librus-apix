"""
Module: timetable_parser

Description:
This module provides functions for parsing and retrieving timetable data from an educational institution's website.

Classes:
    - Period: Represents a period of a class with relevant information.

Functions:
    - get_timetable: Retrieves the timetable for a given week starting from a Monday date.

Exceptions:
    - DateError: Raised when the provided date is not a Monday.
    - ParseError: Raised when there's an error while parsing the timetable.

Usage:
```python
from your_client_module import Client  # import your client module here

# Example usage:
client = Client()  # initialize your client
monday_date = datetime(2024, 5, 13)  # example Monday date
try:
    timetable = get_timetable(client, monday_date)
    for day in timetable:
        for period in day:
            print(period.subject, period.date, period.date_from, period.date_to)
except DateError as e:
    print(e)
except ParseError as e:
    print(e)
```
"""

from typing import List, Dict
from librus_apix.client import Client
from librus_apix.exceptions import ParseError, DateError
from librus_apix.helpers import no_access_check
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class Period:
    """
    Represents a period of a class with relevant information.

    Attributes:
        subject (str): The subject of the class.
        teacher_and_classroom (str): Combined information of teacher and classroom.
        date (str): The date of the period.
        date_from (str): Starting time of the period.
        date_to (str): Ending time of the period.
        weekday (str): The day of the week of the period.
        info (Dict[str, str]): Additional information about the period.
        number (int): The number of the period within a day.
        next_recess_from (str | None): Starting time of the next recess, if any.
        next_recess_to (str | None): Ending time of the next recess, if any.
    """

    subject: str
    teacher_and_classroom: str
    date: str
    date_from: str
    date_to: str
    weekday: str
    info: Dict[str, str]
    number: int
    next_recess_from: str | None
    next_recess_to: str | None


def get_timetable(client: Client, monday_date: datetime) -> List[List[Period]]:
    """
    Retrieves the timetable for a given week starting from a Monday date.

    Args:
        client (Client): An instance of the client class for fetching data.
        monday_date (datetime): The Monday date for the week's timetable.

    Returns:
        List[List[Period]]: A nested list containing periods for each day of the week.

    Raises:
        DateError: If the provided date is not a Monday.
        ParseError: If there's an error while parsing the timetable.
    """
    timetable: List[List[Period]] = []
    if monday_date.strftime("%A") != "Monday":
        raise DateError("You must input a Monday date.")
    sunday = monday_date + timedelta(days=6)
    week = f"{monday_date.strftime('%Y-%m-%d')}_{sunday.strftime('%Y-%m-%d')}"
    post = client.post(client.TIMETABLE_URL, data={"tydzien": week})
    soup = no_access_check(BeautifulSoup(post.text, "lxml"))
    periods = soup.select("table.decorated.plan-lekcji > tr.line1")
    if len(periods) < 1:
        raise ParseError("Error in parsing timetable.")
    recess = soup.select("table.decorated.plan-lekcji > tr.line0")
    for weekday in range(7):
        timetable.append([])
        for period in range(len(periods)):
            [recess_from, recess_to] = [None, None]
            if period <= len(recess) - 1:
                center = recess[period].select_one("td.center")
                if center is None:
                    raise ParseError("Error while parsing timetable (center)")
                [recess_from, recess_to] = [
                    x.strip()
                    for x in center.text.replace("&nbsp;", "").strip().split("-", 1)
                ]
            lesson = periods[period].select(
                'td[id="timetableEntryBox"][class="line1"]'
            )[weekday]
            td_center = periods[period].select_one('td[class="center"]')
            if td_center is None:
                raise ParseError("Error while parsing lesson_number of period")
            lesson_number = int(td_center.text)
            tooltip = lesson.select_one("div.center.plan-lekcji-info")
            a_href = lesson.select_one("a")
            info = {}
            if tooltip is not None:
                if a_href is None:
                    info[tooltip.text.strip()] = ""
                else:
                    attr_dict = {}
                    for attr in (
                        a_href.attrs["title"]
                        .replace("<b>", "")
                        .replace("</b>", "")
                        .replace("\xa0", " ")
                        .split("<br>")
                    ):
                        if len(attr.strip()) > 2:
                            key, value = attr.split(": ", 1)
                            attr_dict[key] = value

                    info[tooltip.text.strip()] = {
                        "teacher_swap": attr_dict.get("Nauczyciel", ""),
                        "subject_swap": attr_dict.get("Przedmiot", ""),
                        "classroom_swap": attr_dict.get("Sala", ""),
                        "date_added": attr_dict.get("Data dodania", ""),
                    }
            date, date_from, date_to = [
                val for key, val in lesson.attrs.items() if key.startswith("data")
            ]
            lesson = lesson.select_one("div.text")
            if lesson is None:
                subject = ""
                teacher_and_classroom = ""
            else:
                subject = lesson.select_one("b")
                subject = subject.text if subject is not None else ""
                teacher_and_classroom = (
                    lesson.text.replace("\xa0", " ")
                    .replace("\n", "")
                    .replace("&nbsp", "")
                    .split("-")
                )
                if len(teacher_and_classroom) >= 2:
                    teacher_and_classroom = "-".join(teacher_and_classroom[1:])
                else:
                    teacher_and_classroom = ""

            weekday_str = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
            p = Period(
                subject,
                teacher_and_classroom,
                date,
                date_from,
                date_to,
                weekday_str,
                info,
                lesson_number,
                recess_from,
                recess_to,
            )
            timetable[weekday].append(p)
    return timetable
