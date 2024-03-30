from ctypes import ArgumentError
import re
from datetime import datetime
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from librus_apix.get_token import get_token, Token
from librus_apix.helpers import no_access_check
from librus_apix.exceptions import TokenError, ParseError
from librus_apix.urls import BASE_URL
from typing import Union, Tuple, List, Dict
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


@dataclass
class GradeDescriptive:
    title: str
    grade: str
    date: str
    href: str
    desc: str
    semester: int
    teacher: str


def get_grades(
    token: Token, sort_by: str = "all"
) -> Tuple[List[Dict[str, Grade]], Dict[str, Gpa], List[Dict[str, GradeDescriptive]]]:
    SORT = {
        "all": "zmiany_logowanie_wszystkie",
        "week": "zmiany_logowanie_tydzien",
        "last_login": "zmiany_logowanie",
    }
    if sort_by not in SORT.keys():
        raise ArgumentError(
            "Wrong value for sort_by it can be either all, week or last_login"
        )

    tr = no_access_check(
        BeautifulSoup(
            token.post(token.GRADES_URL, data={SORT[sort_by]: 1}).text,
            "lxml",
        )
    ).find_all("tr", attrs={"class": ["line0", "line1"], "id": None})
    if len(tr) < 1:
        raise ParseError("Error in parsing grades")

    sem_grades, avg_grades = _extract_grades_numeric(tr)
    sem_grades_desc = _extract_grades_descriptive(tr)
    return sem_grades, avg_grades, sem_grades_desc


def _handle_subject(semester_grades):
    return semester_grades[0].text.replace("\n", "").strip()


def get_desc_and_counts(a, grade, subject) -> Tuple[str, bool]:
    desc = f"Ocena: {grade}\nPrzedmiot: {subject}\n"
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


def _extract_grade_info(a, subject):
    date = re.search("Data:.{11}", a.attrs["title"])
    attr_dict = {}
    for attr in a.attrs["title"].replace("<br/>", "<br>").split("<br>"):
        if len(attr.strip()) > 2:
            key, value = attr.split(": ", 1)
            attr_dict[key] = value
    category = attr_dict.get("Kategoria", "")
    teacher = attr_dict.get("Nauczyciel", "")
    weight = attr_dict.get("Waga", 0)

    if date is None:
        raise ParseError("Error in getting grade's date.")
    grade = a.text.replace("\xa0", "").replace("\n", "")
    desc, counts = get_desc_and_counts(a, grade, subject)

    return (
        grade,
        date.group().split(" ")[1],
        a.attrs["href"],
        desc,
        counts,
        category,
        teacher,
        weight,
    )


def _extract_grades_numeric(table_rows):
    # list containing two dicts (for each semester)
    # key of each semester dict is subject, in each subject there is list of grades
    sem_grades: List[Dict[str, List[Grade]]] = [{}, {}]
    avg_grades = defaultdict(list)

    for box in table_rows:
        if box.select_one("td[class='center micro screen-only']") is None:
            # row without grade data - skip
            continue
        semester_grades = box.select(
            'td[class!="center micro screen-only"]'  # [class!="right"]'
        )
        if len(semester_grades) < 9:
            continue
        average_grades = list(map(lambda x: x.text, box.select("td.right")))
        semesters = [semester_grades[1:4], semester_grades[4:7]]
        subject = _handle_subject(semester_grades)
        for sem, semester in enumerate(semesters):
            if subject not in sem_grades[sem]:
                sem_grades[sem][subject] = []
            for sg in semester:
                grade_a_improved = sg.select("td[class!='center'] > span > span.grade-box > a")
                grade_a = sg.select("td[class!='center'] > span.grade-box > a") + grade_a_improved
                for a in grade_a:
                    (
                        _grade,
                        date,
                        href,
                        desc,
                        counts,
                        category,
                        teacher,
                        weight,
                    ) = _extract_grade_info(a, subject)
                    g = Grade(
                        subject,
                        _grade,
                        counts,
                        date,
                        a.attrs["href"],
                        desc,
                        sem + 1,
                        category,
                        teacher,
                        weight,
                    )
                    sem_grades[sem][subject].append(g)
            avg_gr = (
                average_grades[sem] if len(average_grades) > sem else 0.0
            )  # might happen that the list is empty
            gpa = Gpa(sem + 1, avg_gr, subject)
            avg_grades[subject].append(gpa)
        avg_gr = (
            average_grades[-1] if average_grades else 0.0
        )  # might happen that the list is empty
        avg_grades[subject].append(Gpa(0, avg_gr, subject))

    return sem_grades, avg_grades


def _extract_grades_descriptive(table_rows):
    def get_desc(a, grade, subject) -> str:
        desc = f"Ocena: {grade}\nPrzedmiot: {subject}\n"
        desc += re.sub(
            r"<br*>",
            "\n",
            a.attrs["title"].replace("<br/>", "").replace("<br />", "\n"),
        )
        return desc

    # list containing two dicts (for each semester)
    # key of each semester dict is subject, in each subject there is list of grades
    sem_grades_desc: List[Dict[str, List[GradeDescriptive]]] = [{}, {}]

    for box in table_rows:
        if box.select_one("td[class='micro center screen-only']") is None:
            # row without descriptive grade data - skip
            continue
        semester_grades = box.select(
            'td[class!="micro center screen-only"]'  # [class!="right"]'
        )
        if len(semester_grades) < 3:
            continue
        semesters = [semester_grades[1], semester_grades[2]]
        subject = semester_grades[0].text.replace("\n", "").strip()
        for sem_index, sg in enumerate(semesters):
            if subject not in sem_grades_desc[sem_index]:
                sem_grades_desc[sem_index][subject] = []
            grade_a = sg.select("td[class!='center'] > span.grade-box > a")
            for a in grade_a:
                (
                    _grade,
                    date,
                    href,
                    desc,
                    _,
                    category,
                    teacher,
                    weight,
                ) = _extract_grade_info(a, subject)
                if "javascript" in href:
                    # javascript content is not standard href - clear it
                    href = ""
                g = GradeDescriptive(
                    subject, _grade, date, href, desc, sem_index + 1, teacher
                )
                sem_grades_desc[sem_index][subject].append(g)

    # get semester descriptive grade
    found_grade = False
    summary_title = ""
    summary_desc = ""
    summary_date = ""
    summary_teacher = ""

    parse_next_row = False
    for box in table_rows:
        if parse_next_row:
            parse_next_row = False
            paragraphs = box.find_all("p")
            text_list = [ par.text.strip() for par in paragraphs ]
            summary_desc = "\n".join(text_list).strip()
            found_grade = True
            # description found - break
            # There is no more grades for now (for first semester). Maybe there will be grade for
            # second semester, but the format (structure) of web page is unknown for the moment.
            # #TODO: implement the case for second semester (in future)
            break

        header = box.select_one("th")
        if header:
            # header row found - next row will contain the description
            parse_next_row = True
            title_tag = header.select_one("strong")
            info = title_tag.next_sibling
            summary_title = title_tag.text.strip()
            summary_date = re.findall(r"opublikowano: (.+?) ", info)[0]     # get date only
            summary_teacher = re.findall(r"nauczyciel: (.+?)\)", info)[0]

    if found_grade:
        sem_index = 0
        semester_summary = GradeDescriptive(summary_title, "", summary_date, "",
                                            summary_desc, sem_index + 1, summary_teacher)
        if summary_title not in sem_grades_desc[sem_index]:
            sem_grades_desc[sem_index][summary_title] = []
        sem_grades_desc[sem_index][summary_title].append(semester_summary)

    return sem_grades_desc
