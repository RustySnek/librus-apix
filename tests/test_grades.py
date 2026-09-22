from logging import Logger
from typing import DefaultDict, Union
import pytest
from bs4 import BeautifulSoup
from librus_apix.client import Client
from librus_apix.grades import Gpa, Grade, _extract_grades_descriptive, get_grades


def _test_grade_data(grade: Grade, log: Logger):
    grade_dict = list(grade.__dict__.items())
    strings = grade_dict[:2] + grade_dict[3:6] + grade_dict[7:9]
    for key, val in strings:
        assert isinstance(val, str)
        if val == "":
            log.warning(f"{key} is an empty string")


@pytest.mark.parametrize("opt", ["all", "week", "last_login"])
def test_get_grades(client: Client, opt: str, log: Logger):
    grades, semester_grades, descriptive_grades = get_grades(client, opt)
    assert isinstance(grades, list)
    assert isinstance(descriptive_grades, list)
    assert isinstance(semester_grades, DefaultDict)
    for semester in grades:
        assert isinstance(semester, dict)
        for grades in semester.values():
            for grade in grades:
                assert isinstance(grade, Grade)
                _test_grade_data(grade, log)

    for subject in semester_grades.values():
        for grade in subject:
            assert isinstance(grade, Gpa)
            assert isinstance(grade.semester, int)
            assert grade.semester >= 0
            assert isinstance(grade.gpa, Union[str, float])
            assert isinstance(grade.subject, str)
    assert all(isinstance(semester, dict) for semester in descriptive_grades)

def test_extract_descriptive_grades_old_schema():
    html = """
    <tr class="line1">
        <td class="micro center screen-only"></td>
        <td>Przedmiot</td>
        <td>
            <table>
                <tr>
                    <td class="grade-cell">
                        <span class="grade-box">
                            <a
                                title="Kategoria: Test<br>Data: 2026-09-21<br>Nauczyciel: Nauczyciel<br>Waga: 1<br>Licz do średniej: tak"
                                href="/grade/1"
                            >5</a>
                        </span>
                    </td>
                </tr>
            </table>
        </td>
        <td></td>
    </tr>
    """
    row = BeautifulSoup(html, "lxml").find("tr")
    assert row is not None

    grades = _extract_grades_descriptive([row])

    assert len(grades[0]["Przedmiot"]) == 1
    grade = grades[0]["Przedmiot"][0]
    assert grade.grade == "5"
    assert grade.date == "2026-09-21"
    assert grade.teacher == "Nauczyciel"
    assert grade.semester == 1
    assert grade.href == "/grade/1"


def test_extract_descriptive_grades_new_schema():
    html = """
    <tr class="studentRow line1">
        <td class="micro center screen-only"></td>
        <td>Przedmiot</td>
        <td class="gradesCell" data-semester="1">
            <span
                class="grade-box tooltip"
                title="Obszar: Komunikacja<br>Data: 2026-09-22 (wt.)<br>Nauczyciel: Nauczyciel<br>Ocena ze skali: 6<br>Treść oceny: <br>Dodał: Nauczyciel<br>Komentarz: Test<br/>"
            ><span class="ocena">6</span></span>
        </td>
        <td class="gradesCell" data-semester="2"></td>
    </tr>
    """
    row = BeautifulSoup(html, "lxml").find("tr")
    assert row is not None

    grades = _extract_grades_descriptive([row])

    assert len(grades[0]["Przedmiot"]) == 1
    grade = grades[0]["Przedmiot"][0]
    assert grade.grade == "6"
    assert grade.date == "2026-09-22"
    assert grade.teacher == "Nauczyciel"
    assert grade.semester == 1
    assert grade.href == ""
    assert grades[1]["Przedmiot"] == []
