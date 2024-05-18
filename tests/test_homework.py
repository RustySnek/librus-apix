from datetime import datetime, timedelta
from logging import Logger
import pytest

from librus_apix.client import Client
from librus_apix.homework import Homework, get_homework, homework_detail


def _test_homework_data(hw: Homework, log: Logger):
    for key, val in hw.__dict__.items():
        assert isinstance(val, str)
        if val == "":
            log.warning(f"{key} is an empty string")


@pytest.fixture
def _get_homework(client: Client):
    now = datetime.now()
    homework = get_homework(
        client,
        now.strftime("%Y-%m-%d"),
        (now + timedelta(days=30)).strftime("%Y-%m-%d"),
    )
    return homework


def test_get_homework(_get_homework, log: Logger):
    assert isinstance(_get_homework, list)
    for h in _get_homework:
        assert isinstance(h, Homework)
        _test_homework_data(h, log)


def test_get_homework_detail(_get_homework, client: Client):
    if len(_get_homework) == 0:
        pytest.skip("No homework to check")
    content = homework_detail(client, _get_homework[0].href)
    assert isinstance(content, dict)
