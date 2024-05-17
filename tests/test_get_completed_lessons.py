from datetime import datetime, timedelta
from logging import Logger
from typing import Union
import pytest

from librus_apix.completed_lessons import Lesson, get_completed, get_max_page_number
from librus_apix.get_token import Token


def _test_completed_lesson_data(lesson: Lesson, log: Logger):
    lesson_dict = list(lesson.__dict__.items())
    strings = lesson_dict[:7] + lesson_dict[8:]
    if isinstance(lesson.lesson_number, int):
        assert lesson.lesson_number >= 0
    else:
        assert isinstance(lesson.lesson_number, str)
    for key, val in strings:
        assert isinstance(val, str)
        if val == "":
            log.warning(f"{key} is an empty string")


def test_completed_lessons_max_page(token: Token):
    now = datetime.now()
    max_page = get_max_page_number(
        token, now.strftime("%Y-%m-%d"), (now + timedelta(days=30)).strftime("%Y-%m-%d")
    )
    assert isinstance(max_page, int)
    assert max_page >= 0


def test_get_completed_lessons(token: Token, log: Logger):
    now = datetime.now()
    lessons = get_completed(
        token, now.strftime("%Y-%m-%d"), (now + timedelta(days=30)).strftime("%Y-%m-%d")
    )
    assert isinstance(lessons, list)
    for lesson in lessons:
        assert isinstance(lesson, Lesson)
        _test_completed_lesson_data(lesson, log)
