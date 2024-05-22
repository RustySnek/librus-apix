from logging import Logger
from typing import List
import pytest
from librus_apix.notifications import Notification
from librus_apix.client import Client
from librus_apix.notifications import get_notifications


def _test_notification_data(notify: Notification, log: Logger):
    assert isinstance(notify.destination, str)
    assert isinstance(notify.amount, int)
    assert notify.amount > 0
    if notify.destination == "":
        log.warning(f"Notification ({notify.amount}) destination is empty!")


def test_student_information(client: Client, log: Logger):
    notifications = get_notifications(client)
    assert isinstance(notifications, List)
    for notify in notifications:
        assert isinstance(notify, Notification)
        _test_notification_data(notify, log)
