from typing import DefaultDict
import pytest
from librus_apix.grades import get_grades


@pytest.mark.parametrize("opt", ["all", "week", "last_login"])
def test_get_grades(token, opt):
    grades, semester_grades, descriptive_grades = get_grades(token, opt)
    assert isinstance(grades, list)
    assert isinstance(descriptive_grades, list)
    assert isinstance(semester_grades, DefaultDict)
    assert all(isinstance(semester, dict) for semester in grades)
    assert all(isinstance(semester, dict) for semester in descriptive_grades)
