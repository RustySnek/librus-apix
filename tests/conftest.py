import pytest
from librus_apix.get_token import Token


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
def token(request):
    token = request.config.getoption("token")
    if token is None:
        mock_key = "what:ever"
        base = request.config.getoption("mock_url")
        grades = base + "/grades.html"
        timetable = base + "/timetable.html"
        messages = base + "/messages.html"
        sent_messages = base + "/sent_messages.html"
        return Token(
            API_Key=mock_key,
            base_url=base,
            grades_url=grades,
            timetable_url=timetable,
            message_url=messages,
            send_message_url=sent_messages,
        )
    else:
        return Token(token)
