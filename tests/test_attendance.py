from logging import Logger
import pytest

from librus_apix.attendance import Attendance, get_attendance
from librus_apix.get_token import Token


def _test_attendance_data(attendance: Attendance, log: Logger):
    attendance_dict = list(attendance.__dict__.items())
    strings = attendance_dict[:2] + attendance_dict[3:5] + attendance_dict[8:]
    assert isinstance(attendance.semester, int)
    assert attendance.semester >= 0
    assert isinstance(attendance.period, int)
    assert attendance.period >= 0
    assert isinstance(attendance.excursion, bool)
    for key, val in strings:
        assert isinstance(val, str)
        if val == "":
            log.warning(f"{key} is an empty string")


@pytest.mark.parametrize("opt", ["all", "week", "last_login"])
def test_get_attendance(token: Token, opt: str, log: Logger):
    first, second = get_attendance(token, opt)
    assert isinstance(first, list)
    assert isinstance(second, list)
    attendance = first + second
    for a in attendance:
        assert isinstance(a, Attendance)
        _test_attendance_data(a, log)
