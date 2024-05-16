from datetime import datetime, timedelta
import pytest

from librus_apix.homework import Homework, get_homework, homework_detail


@pytest.fixture
def _get_homework(token):
    now = datetime.now()
    homework = get_homework(
        token, now.strftime("%Y-%m-%d"), (now + timedelta(days=30)).strftime("%Y-%m-%d")
    )
    return homework


def test_get_homework(_get_homework):
    assert isinstance(_get_homework, list)
    assert all(isinstance(h, Homework) for h in _get_homework)


def test_get_homework_detail(_get_homework, token):
    if len(_get_homework) == 0:
        pytest.skip("No homework to check")
    content = homework_detail(token, _get_homework[0].href)
    assert isinstance(content, dict)
