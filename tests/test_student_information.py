import pytest
from librus_apix.student_information import StudentInformation, get_student_information

def test_student_information(token):
    info = get_student_information(token)
    assert isinstance(info, StudentInformation)
