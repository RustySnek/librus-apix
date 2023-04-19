from ctypes import ArgumentError
import re
from datetime import datetime
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from librus_apix.get_token import get_token, Token
from librus_apix.helpers import no_access_check
from librus_apix.exceptions import TokenError, ParseError
from librus_apix.urls import BASE_URL
from typing import Union
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Gpa:
    semester: int
    gpa: float
    subject: str

@dataclass
class Grade:
    title: str
    grade: str
    counts: bool
    date: str
    href: str
    desc: str
    semester: int
    category: str
    teacher: str
    weight: int

    @property
    def value(self) -> Union[float, str]:
        if self.counts is False:
            return "Does not count"
        if len(self.grade) > 1:
            grade_value = float(self.grade[0]) + float(
                self.grade[1].replace("+", ".5").replace("-", "-0.25")
            )
        else:
            grade_value = float(self.grade)
        return grade_value


def get_grades(token: Token, sort_by: str = 'all') -> tuple[dict[int, dict[str ,Grade]], dict[str, Gpa]]:
    def get_desc_and_counts(a, grade, subject) -> list[str, bool]:
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
    SORT = {
        "all": 'zmiany_logowanie_wszystkie',
        "week": 'zmiany_logowanie_tydzien',
        "last_login": 'zmiany_logowanie'
            }
    if sort_by not in SORT.keys():
        raise ArgumentError("Wrong value for sort_by it can be either all, week or last_login")
    sem_grades: dict[int, dict[str, list[Grade]]] = {1: {}, 2: {}}
    avg_grades = defaultdict(list)

    tr = no_access_check(
            BeautifulSoup(token.post(BASE_URL + "/przegladaj_oceny/uczen", data={SORT[sort_by]: 1}).text, "lxml")
    ).find_all("tr", attrs={"class": ["line0", "line1"], "id": None})
    if len(tr) < 1:
        raise ParseError("Error in parsing grades")
    for box in tr:
        if box.select_one("td[class='center micro screen-only']") is None:
            continue
        semester_grades = box.select(
            'td[class!="center micro screen-only"]'#[class!="right"]'
        )
        if len(semester_grades) < 9:
            continue
        average_grades = list(map(lambda x: x.text, box.select('td.right')))
        semesters = [semester_grades[1:4], semester_grades[4:7]]
        subject = semester_grades[0].text.replace("\n", "").strip()
        for sem, semester in enumerate(semesters):
            if subject not in sem_grades[sem + 1]:
                sem_grades[sem + 1][subject] = []
            for sg in semester:
                grade_a = sg.select("td[class!='center'] > span.grade-box > a")
                for a in grade_a:
                    date = re.search("Data:.{11}", a.attrs["title"])
                    attr_dict = {}
                    for attr in a.attrs['title'].replace('<br/>', '<br>').split('<br>'):
                        if len(attr.strip()) > 2:
                            key, value = attr.split(': ')
                            attr_dict[key] = value
                    category = attr_dict['Kategoria']
                    teacher = attr_dict['Nauczyciel']
                    weight = 0
                    try:
                        weight = attr_dict['Waga']
                    except:
                        pass

                    if date is None:
                        raise ParseError("Error in getting grade's date.")

                    _grade = a.text.replace("\xa0", "").replace("\n", "")
                    desc, counts = get_desc_and_counts(a, _grade, subject)
                    g = Grade(
                        subject,
                        _grade,
                        counts,
                        date.group().split(" ")[1],
                        a.attrs["href"],
                        desc,
                        sem + 1,
                        category,
                        teacher,
                        weight
                    )
                    sem_grades[sem + 1][subject].append(g)
            gpa = Gpa(sem+1, average_grades[sem], subject)
            avg_grades[subject].append(gpa)
        avg_grades[subject].append(Gpa(0, average_grades[-1], subject))
    return sem_grades, avg_grades
