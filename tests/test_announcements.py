from logging import Logger
import pytest

from librus_apix.announcements import Announcement, get_announcements
from librus_apix.get_token import Token


def _test_announcement_data(announcement: Announcement, log: Logger):
    strings = announcement.__dict__.items()
    for key, val in strings:
        assert isinstance(val, str)
        if val == "":
            log.warning(f"{key} is an empty string")


def test_get_announcements(token: Token, log: Logger):
    announcements = get_announcements(token)
    assert isinstance(announcements, list)
    for a in announcements:
        assert isinstance(a, Announcement)
        _test_announcement_data(a, log)
