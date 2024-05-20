import pytest
from librus_apix.client import Client, Token
import logging


@pytest.fixture(scope="session")
def log():
    return logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption(
        "--token",
        action="store",
        default=None,
        help="Your token generated by librus_apix.get_token.get_token(user, pass)",
    )
    parser.addoption(
        "--mock_url", action="store", default="http://localhost:8000", help="mock url"
    )


@pytest.fixture(scope="session")
def client(request) -> Client:
    token_key = request.config.getoption("token")
    token: Token = Token(API_Key=token_key)
    if token_key is None:
        token: Token = Token(API_Key="what:ever")
        base = request.config.getoption("mock_url")
        grades = base + "/grades.html"
        timetable = base + "/timetable.html"
        messages = base + "/messages.html"
        sent_messages = base + "/sent_messages.html"
        attendance = base + "/attendance.html"
        announcements = base + "/announcements.html"
        completed_lessons = base + "/completed.html"
        schedule = base + "/schedule.html"
        student_info = base + "/student_info.html"
        homework = base + "/homework.html"
        hw_detail = base + "/homework/"
        notifications = base + "/notifications.html"

        return Client(
            token=token,
            base_url=base,
            grades_url=grades,
            timetable_url=timetable,
            message_url=messages,
            send_message_url=sent_messages,
            announcements_url=announcements,
            attendance_url=attendance,
            completed_lessons_url=completed_lessons,
            schedule_url=schedule,
            info_url=student_info,
            homework_url=homework,
            homework_details_url=hw_detail,
            index_url=notifications
        )
    else:
        return Client(token)
