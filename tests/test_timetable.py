from logging import Logger
from typing import Union
import pytest
from datetime import datetime, timedelta
from librus_apix.exceptions import DateError
from librus_apix.timetable import get_timetable, Period

today = datetime.now()

current_weekday = today.weekday()
most_recent_monday = today - timedelta(days=current_weekday)
monday_from_last_month = most_recent_monday - timedelta(weeks=4)
monday_from_next_month = most_recent_monday + timedelta(weeks=4)


def _test_period_data(period: Period, log: Logger):
    period_dict = list(period.__dict__.items())
    strings = period_dict[:6]
    assert isinstance(period.info, dict)
    assert isinstance(period.number, int)
    assert isinstance(period.next_recess_from, Union[str, None])
    assert isinstance(period.next_recess_to, Union[str, None])
    assert period.number >= 0
    for _, val in strings:
        assert isinstance(val, str)


@pytest.mark.parametrize(
    "monday",
    [
        most_recent_monday,
        monday_from_last_month,
        monday_from_next_month,
    ],
)
def test_get_timetable(token, monday, log: Logger):
    timetable = get_timetable(token, monday)
    assert isinstance(timetable, list)
    for weekday in timetable:
        assert isinstance(weekday, list)
        for period in weekday:
            assert isinstance(period, Period)
            _test_period_data(period, log)


def test_wrong_date_timetable(token):
    non_monday = most_recent_monday + timedelta(days=1)
    with pytest.raises(DateError):
        get_timetable(token, non_monday)
