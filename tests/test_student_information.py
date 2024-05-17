from logging import Logger
from typing import Union
import pytest
from librus_apix.get_token import Token
from librus_apix.student_information import StudentInformation, get_student_information


def _test_student_data(si: StudentInformation, log: Logger):
    si_dict = list(si.__dict__.items())
    strings = si_dict[:2] + si_dict[3:]
    assert isinstance(si.number, int)
    assert si.number >= 0

    for key, val in strings:
        assert isinstance(val, Union[int, str])
        if val == "":
            log.warning(f"{key} is an empty string")


def test_student_information(token: Token, log: Logger):
    info = get_student_information(token)
    assert isinstance(info, StudentInformation)
    _test_student_data(info, log)
