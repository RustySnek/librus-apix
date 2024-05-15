from datetime import datetime, timedelta
import pytest

from librus_apix.completed_lessons import get_completed, get_max_page_number


def test_completed_lessons_max_page(token):
    now = datetime.now()
    max_page = get_max_page_number(
        token, now.strftime("%Y-%m-%d"), (now + timedelta(days=30)).strftime("%Y-%m-%d")
    )
    assert isinstance(max_page, int)
    assert max_page >= 0


def test_get_completed_lessons(token):
    now = datetime.now()
    lessons = get_completed(
        token, now.strftime("%Y-%m-%d"), (now + timedelta(days=30)).strftime("%Y-%m-%d")
    )
    assert isinstance(lessons, list)
