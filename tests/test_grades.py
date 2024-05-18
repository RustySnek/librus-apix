from logging import Logger
from typing import DefaultDict, Union
import pytest
from librus_apix.client import Client
from librus_apix.grades import Gpa, Grade, get_grades


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
