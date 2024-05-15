from datetime import datetime, timedelta
import pytest

from librus_apix.schedule import get_schedule

now = datetime.now()


@pytest.mark.parametrize("year", [now.year])
@pytest.mark.parametrize(
    "month",
    [now.month, (now + timedelta(days=31)).month, (now - timedelta(days=31)).month],
)
def test_get_schedule_with_empty_days(token, year, month):
    schedule = get_schedule(token, month, year, True)
    assert isinstance(schedule, dict)
    assert len(schedule) > 20


@pytest.mark.parametrize("year", [now.year])
@pytest.mark.parametrize(
    "month",
    [now.month, (now + timedelta(days=31)).month, (now - timedelta(days=31)).month],
)
def test_non_empty_schedule(token, year, month):
    schedule = get_schedule(token, month, year, False)
    assert isinstance(schedule, dict)
    assert all(len(day) > 0 for day in schedule.values())
