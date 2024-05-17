from datetime import datetime, timedelta
from logging import Logger
from typing import Union
import pytest

from librus_apix.schedule import Event, get_schedule

now = datetime.now()


def _test_event_data(event: Event, log: Logger):
    event_dict = event.__dict__.items()
    strings = {key: val for key, val in event_dict if key != "data"}
    assert isinstance(event.data, dict)
    for key, val in strings.items():
        assert isinstance(val, Union[int, str])
        if val == "":
            log.warning(f"{key} is an empty string")


@pytest.mark.parametrize("year", [now.year])
@pytest.mark.parametrize(
    "month",
    [now.month, (now + timedelta(days=31)).month, (now - timedelta(days=31)).month],
)
def test_get_schedule_with_empty_days(token, year, month, log: Logger):
    schedule = get_schedule(token, month, year, True)
    assert isinstance(schedule, dict)
    assert len(schedule) > 20
    for day in schedule.values():
        all(_test_event_data(event, log) for event in day)


@pytest.mark.parametrize("year", [now.year])
@pytest.mark.parametrize(
    "month",
    [now.month, (now + timedelta(days=31)).month, (now - timedelta(days=31)).month],
)
def test_non_empty_schedule(token, year, month, log: Logger):
    schedule = get_schedule(token, month, year, False)
    assert isinstance(schedule, dict)
    for day in schedule.values():
        assert len(day) > 0
        all(_test_event_data(event, log) for event in day)
