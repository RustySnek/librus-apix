import pytest

from librus_apix.attendance import Attendance, get_attendance


@pytest.mark.parametrize("opt", ["all", "week", "last_login"])
def test_get_attendance(token, opt):
    first, second = get_attendance(token, opt)
    assert isinstance(first, list)
    assert isinstance(second, list)
    attendance = first + second
    assert all(isinstance(a, Attendance) for a in attendance)
