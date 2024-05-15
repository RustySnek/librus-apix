import pytest

from librus_apix.announcements import Announcement, get_announcements


def test_get_announcements(token):
    announcements = get_announcements(token)
    assert isinstance(announcements, list)
    assert all(isinstance(a, Announcement) for a in announcements)
