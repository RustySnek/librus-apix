import pytest
from datetime import datetime, timedelta
from librus_apix.exceptions import DateError
from librus_apix.timetable import get_timetable, Period

today = datetime.now()

current_weekday = today.weekday()
most_recent_monday = today - timedelta(days=current_weekday)
monday_from_last_month = most_recent_monday - timedelta(weeks=4)
monday_from_next_month = most_recent_monday + timedelta(weeks=4)


@pytest.mark.parametrize(
    "monday",
    [
        most_recent_monday,
        monday_from_last_month,
        monday_from_next_month,
    ],
)
def test_get_timetable(token, monday):
    timetable = get_timetable(token, monday)
    assert isinstance(timetable, list)
    for weekday in timetable:
        assert isinstance(weekday, list)
        assert all(isinstance(period, Period) for period in weekday)


def test_wrong_date_timetable(token):
    non_monday = most_recent_monday + timedelta(days=1)
    with pytest.raises(DateError):
        get_timetable(token, non_monday)
