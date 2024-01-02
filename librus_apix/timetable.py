from typing import List, Dict
from librus_apix.get_token import Token
from librus_apix.exceptions import ParseError, DateError
from librus_apix.helpers import no_access_check
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class Period:
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


def get_timetable(token: Token, monday_date: datetime) -> List[List[Period]]:
    timetable: List[List[Period]] = []
    if monday_date.strftime("%A") != "Monday":
        raise DateError("You must input a Monday date.")
    sunday = monday_date + timedelta(days=6)
    week = f"{monday_date.strftime('%Y-%m-%d')}_{sunday.strftime('%Y-%m-%d')}"
    post = token.post(token.TIMETABLE_URL, data={"tydzien": week})
    soup = no_access_check(BeautifulSoup(post.text, "lxml"))
    periods = soup.select("table.decorated.plan-lekcji > tr.line1")
    if len(periods) < 1:
        raise ParseError("Error in parsing timetable.")
    recess = soup.select("table.decorated.plan-lekcji > tr.line0")
    for weekday in range(7):
        timetable.append([])
        for period in range(len(periods)):
            [recess_from, recess_to] = (
                [
                    x.strip()
                    for x in recess[period]
                    .select_one("td.center")
                    .text.replace("&nbsp;", "")
                    .strip()
                    .split("-")
                ]
                if period <= len(recess) - 1
                else [None, None]
            )
            lesson = periods[period].select(
                'td[id="timetableEntryBox"][class="line1"]'
            )[weekday]
            lesson_number = int(periods[period].select_one('td[class="center"]').text)
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
            try:
                subject = lesson.select_one("b").text
                teacher_and_classroom = "-".join(
                    lesson.text.replace("\xa0", " ")
                    .replace("\n", "")
                    .replace("&nbsp", "")
                    .split("-")[1:]
                )

            except:
                subject = ""
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
