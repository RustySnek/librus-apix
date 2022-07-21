import re
from datetime import datetime
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from librus_apix.get_token import get_token, Token
from librus_apix.urls import BASE_URL
from typing import Union
from dataclasses import dataclass

@dataclass
class Grade:
    title: str
    grade: str
    counts: bool
    date: str
    href: str
    desc: str
    semester: int
    value: Union[float, str] = 0.0,

    @property
    def value(self):
        if self.counts is False:
            return "Does not count"
        if len(self.grade) > 1:
            grade_value = float(self.grade[0]) + float(
                self.grade[1].replace("+", ".5").replace("-", "-0.25")
            )
        else:
            grade_value = float(self.grade)
        return grade_value


def get_grades(token: Token) -> dict[str, list[Grade]]:
    def get_desc_and_counts(a, grade, subject):
        desc = f"Ocena: {_grade}\nPrzedmiot: {subject}\n"
        desc += re.sub(
            r"<br*>",
            "\n",
            a.attrs["title"].replace("<br/>", "").replace("<br />", "\n"),
        )
        gpacount = re.search("Licz do średniej: [a-zA-Z]{3}", desc)
        counts = False
        if gpacount and gpacount[0].split(": ")[1] == "tak":
            counts = True
        return desc, counts

    grades: dict[str, list[Grade]] = {}
    sem_grades: dict[str, dict[str, list[Grade]]] = {}
    tr = BeautifulSoup(
        token.get(BASE_URL + "/przegladaj_oceny/uczen").text, "lxml"
    ).find_all("tr", attrs={"class": ["line0", "line1"], "id": None})
    if len(tr) < 1:
        return {'error': 'Malformed token'}, 401
    for box in tr:
        if box.select_one("td[class='center micro screen-only']") is None:
            continue
        semester_grades = box.select(
            'td[class!="center micro screen-only"][class!="right"]'
        )
        if len(semester_grades) < 9:
            continue
        # first_avg, second_avg, gpa = box.select('td.right')
        semesters = [semester_grades[1:4], semester_grades[4:7]]
        subject = semester_grades[0].text.replace("\n", "").strip()
        for sem, semester in enumerate(semesters):
            for sg in semester:
                if sem + 1 not in sem_grades:
                    sem_grades[sem + 1] = {}
                grade_a = sg.select("span.grade-box > a")
                for a in grade_a:
                    date = re.search("Data:.{11}", a.attrs["title"])
                    if date is None:
                        raise Exception("Error in getting grade's date.")

                    _grade = a.text.replace("\xa0", "").replace("\n", "")
                    desc, counts = get_desc_and_counts(a, _grade, subject)
                    g = Grade(
                        subject,
                        _grade,
                        counts,
                        date.group().split(" ")[1],
                        a.attrs["href"],
                        desc,
                        sem+1,
                    )
                    if subject not in sem_grades[sem + 1]:
                        sem_grades[sem + 1][subject] = []
                    sem_grades[sem + 1][subject].append(g)
    return sem_grades, 200
