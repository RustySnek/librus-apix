"""
This module defines functions and data classes for retrieving and managing grade-related data from the Librus API.

Classes:
    - Gpa: Represents the semestral grade for a specific semester and subject.
    - Grade: Represents a single grade entry with detailed information.
    - GradeDescriptive: Represents a descriptive grade entry with detailed information.

Functions:
    - get_grades: Fetches and returns the grades, semestral averages, and descriptive grades from Librus.

Usage:
```python
from librus_apix.grades import get_grades

try:
    # Fetch grades data
    numeric_grades, average_grades, descriptive_grades = get_grades(client, sort_by="all")
    # Process the grades data as required
    ...
except ArgumentError as e:
    # Handle invalid argument error
    ...
except ParseError as e:
    # Handle parse error
    ...
```
"""

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, List, Tuple, Union

from bs4 import BeautifulSoup, Tag

from librus_apix.client import Client
from librus_apix.exceptions import ArgumentError, ParseError
from librus_apix.helpers import no_access_check


@dataclass
class Gpa:
    """
    Represents the Semestral Grade for a specific semester and subject.

    Attributes:
        semester (int): The semester number (e.g., 1 for first semester, 2 for second semester).
        gpa (float | str): The GPA value, which can be a float or a "-" string meaning it's empty.
        subject (str): The subject for which the GPA is calculated.
    """

    semester: int
    gpa: float | str
    subject: str


@dataclass
class Grade:
    """
    Represents a single grade entry with detailed information.

    Attributes:
        title (str): The title of the grade.
        grade (str): The grade string value (e.g., '2', '4+', etc.).
        value (float): Property function. Returns calculated float of grade. (e.g., '4.5 for 4+', '2.75 for 3-')
        counts (bool): Indicates whether the grade counts towards the GPA.
        date (str): The date when the grade was given.
        href (str): A URL suffix associated with the grade.
        desc (str): A detailed description of the grade.
        semester (int): The semester number (e.g., 1 for first semester, 2 for second semester).
        category (str): The category of the grade (e.g., 'Homework', 'Exam').
        teacher (str): The name of the teacher who gave the grade.
        weight (int): The weight of the grade in calculating the final score.
    """

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
        """
        Calculates and returns the numeric value of the grade based on its string representation.

        Returns:
            Union[float, str]: The numeric value of the grade or a string indicating it doesn't count.
        Raises:
            ValueError: if grade's format is invalid ex. A+, B+ instead of 5+, 4+
        """
        if self.counts is False:
            return "Does not count"
        try:
            if len(self.grade) > 1:
                grade_value = float(self.grade[0]) + float(
                    self.grade[1].replace("+", ".5").replace("-", "-0.25")
                )
            else:
                grade_value = float(self.grade)
            return grade_value
        except ValueError:
            raise ValueError("Invalid grade format in .value property func")


@dataclass
class GradeDescriptive:
    title: str
    grade: str
    date: str
    href: str
    desc: str
    semester: int
    teacher: str


def get_grades(client: Client, sort_by: str = "all") -> Tuple[
    List[DefaultDict[str, List[Grade]]],
    DefaultDict[str, List[Gpa]],
    List[DefaultDict[str, List[GradeDescriptive]]],
]:
    """
    Fetches and returns the grades, semestral averages and descriptive grades from librus.

    Args:
        client (Client): The client object used to interact with the server.
        sort_by (str): The criteria to sort grades. Can be 'all', 'week', or 'last_login'.

    Returns:
        Tuple: A tuple containing lists of numeric and descriptive grades, and GPA information.

    Raises:
        ArgumentError: If an invalid sort_by value is provided.
        ParseError: If there is an error in parsing the grades.
    """
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
            client.post(client.GRADES_URL, data={SORT[sort_by]: "1"}).text,
            "lxml",
        )
    ).find_all("tr", attrs={"class": ["line0", "line1"], "id": None})
    if len(tr) < 1:
        raise ParseError("Error in parsing grades")

    sem_grades, avg_grades = _extract_grades_numeric(tr)
    sem_grades_desc = _extract_grades_descriptive(tr)
    return sem_grades, avg_grades, sem_grades_desc


def _handle_subject(semester_grades) -> str:
    return semester_grades[0].text.replace("\n", "").strip()


def _get_desc_and_counts(a: Tag, grade: str, subject: str) -> Tuple[str, bool]:
    desc = f"Ocena: {grade}\nPrzedmiot: {subject}\n"
    desc += re.sub(
        r"<br*>",
        "\n",
        a.attrs.get("title", "").replace("<br/>", "").replace("<br />", "\n"),
    )
    gpacount = re.search("Licz do średniej: [a-zA-Z]{3}", desc)
    counts = False
    if gpacount is not None:
        pair = gpacount[0].split(": ")
        if len(pair) >= 2 and pair[1] == "tak":
            counts = True
    return desc, counts


def _extract_grade_info(
    a: Tag, subject: str
) -> Tuple[str, str, str, str, bool, str, str, int]:
    date = re.search("Data:.{11}", a.attrs.get("title", ""))
    if date is None:
        raise ParseError("Error in getting grade's date.")

    attr_dict = {}
    for attr in a.attrs["title"].replace("<br/>", "<br>").split("<br>"):
        if len(attr.strip()) >= 2:
            key, value = attr.split(": ", 1)
            attr_dict[key] = value
    category: str = attr_dict.get("Kategoria", "")
    teacher: str = attr_dict.get("Nauczyciel", "")
    weight: int = int(attr_dict.get("Waga", 0))

    grade = a.text.replace("\xa0", "").replace("\n", "")
    desc, counts = _get_desc_and_counts(a, grade, subject)
    date = date.group().split(" ")
    date = date[1] if len(date) >= 2 else " ".join(date)
    return (
        grade,
        date,
        a.attrs.get("href", ""),
        desc,
        counts,
        category,
        teacher,
        weight,
    )


def _extract_grades_numeric(
    table_rows: List[Tag],
) -> Tuple[List[DefaultDict[str, List[Grade]]], DefaultDict[str, List[Gpa]]]:
    # list containing two dicts (for each semester)
    # key of each semester dict is subject, in each subject there is list of grades
    sem_grades: List[DefaultDict[str, List[Grade]]] = [
        defaultdict(list) for _ in range(2)
    ]  # 2 semesters
    avg_grades: DefaultDict[str, List[Gpa]] = defaultdict(list)

    for box in table_rows:
        if box.select_one("td[class='center micro screen-only']") is None:
            # row without grade data - skip
            continue
        semester_grades = box.select('td[class!="center micro screen-only"]')
        if len(semester_grades) < 9:
            continue
        average_grades = list(map(lambda x: x.text, box.select("td.right")))
        semesters = [semester_grades[1:4], semester_grades[4:7]]
        subject = _handle_subject(semester_grades)
        for semester_number, semester in enumerate(semesters):
            if subject not in sem_grades[semester_number]:
                sem_grades[semester_number][subject] = []
            for sg in semester:
                grade_a_improved = sg.select(
                    "td[class!='center'] > span > span.grade-box > a"
                )
                grade_a = (
                    sg.select("td[class!='center'] > span.grade-box > a")
                    + grade_a_improved
                )
                for a in grade_a:
                    (
                        _grade,
                        date,
                        _href,
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
                        a.attrs.get("href", ""),
                        desc,
                        semester_number + 1,
                        category,
                        teacher,
                        weight,
                    )
                    sem_grades[semester_number][subject].append(g)
            avg_gr = (
                average_grades[semester_number]
                if len(average_grades) >= semester_number
                else 0.0
            )  # might happen that the list is empty
            gpa = Gpa(semester_number + 1, avg_gr, subject)
            avg_grades[subject].append(gpa)
        avg_gr = (
            average_grades[-1] if len(average_grades) > 0 else 0.0
        )  # might happen that the list is empty
        avg_grades[subject].append(Gpa(0, avg_gr, subject))

    return sem_grades, avg_grades


def _extract_grades_descriptive(
    table_rows: List[Tag],
) -> List[DefaultDict[str, List[GradeDescriptive]]]:
    # list containing two dicts (for each semester)
    # key of each semester dict is subject, in each subject there is list of grades
    sem_grades_desc: List[DefaultDict[str, List[GradeDescriptive]]] = [
        defaultdict(list) for _ in range(2)
    ]  # 2 semesters

    for box in table_rows:
        if box.select_one("td[class='micro center screen-only']") is None:
            # row without descriptive grade data - skip
            continue
        semester_grades = box.select('td[class!="micro center screen-only"]')
        if len(semester_grades) < 3:
            continue
        semesters = [semester_grades[1], semester_grades[2]]
        subject = semester_grades[0].text.replace("\n", "").strip()
        for sem_index, sg in enumerate(semesters):
            grade_a = sg.select("td[class!='center'] > span.grade-box > a")
            for a in grade_a:
                (
                    _grade,
                    date,
                    href,
                    desc,
                    _,
                    _category,
                    teacher,
                    _weight,
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
            text_list = [par.text.strip() for par in paragraphs]
            summary_desc = "\n".join(text_list).strip()
            found_grade = True
            # description found - break
            # There is no more grades for now (for first semester). Maybe there will be grade for
            # second semester, but the format (structure) of web page is unknown for the moment.
            # #TODO: implement the case for second semester (in future)
            break

        header = box.select_one("th")
        if header and header.select_one("strong") is not None:
            # header row found - next row will contain the description
            parse_next_row = True
            title_tag = header.select_one("strong")
            if title_tag is None:
                continue
            info = title_tag.next_sibling
            if info is None:
                continue
            summary_title = title_tag.text.strip()
            summary_date = re.findall(r"opublikowano: (.+?) ", info.text)[
                0
            ]  # get date only
            summary_teacher = re.findall(r"nauczyciel: (.+?)\)", info.text)[0]

    if found_grade:
        sem_index = 0
        semester_summary = GradeDescriptive(
            summary_title,
            "",
            summary_date,
            "",
            summary_desc,
            sem_index + 1,
            summary_teacher,
        )
        if summary_title not in sem_grades_desc[sem_index]:
            sem_grades_desc[sem_index][summary_title] = []
        sem_grades_desc[sem_index][summary_title].append(semester_summary)

    return sem_grades_desc
