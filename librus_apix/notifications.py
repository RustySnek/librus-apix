"""
This module provides functionality to interact with the Librus site and extract notifications from the user's dashboard.

The notification bubbles are bound to token, and their amount doesn't change unless you retrieve a new Token, hence we have to
request every individual last_login endpoint and retrieve stuff from there.

Classes:
    - NotificationAmount: Represents a notification with a destination and an amount.
    - NotificationData: Represents data of various notifications including grades, attendance, messages, announcements, schedule, and homework.
    - NotificationIds: Represents the IDs of various notifications to track seen notifications.

Functions:
    - get_initial_notification_data(client: Client) -> Tuple[NotificationData, NotificationIds]: Fetches and parses the initial notification data and their IDs for a new token.
    - get_new_notification_data(client: Client, seen_notifications: NotificationIds) -> Tuple[NotificationData, NotificationIds]: Fetches and parses new notifications using NotificationIds, returns data and updates seen notification IDs.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from hashlib import md5
from typing import Any, DefaultDict, List, Tuple

from bs4 import BeautifulSoup, Tag

from librus_apix.announcements import Announcement, get_announcements
from librus_apix.attendance import Attendance, get_attendance
from librus_apix.client import Client
from librus_apix.exceptions import ParseError
from librus_apix.grades import Grade, get_grades
from librus_apix.helpers import no_access_check
from librus_apix.homework import Homework, get_homework
from librus_apix.messages import Message, get_received
from librus_apix.schedule import RecentEvent, get_recently_added_schedule


@dataclass
class NotificationAmount:
    """
    Represents a notification with a destination identifier name and an amount.

    Attributes:
        name (str): Str representation of name ex: Oceny
        destination (str): endpoint
        amount (int): The count of notifications for the given destination.
    """

    name: str
    destination: str
    amount: int


def get_new_token_notification_amounts(client: Client) -> List[NotificationAmount]:
    """
    Fetches and parses notification amounts from the user's dashboard on the Librus platform.

    Args:
        client (Client): An instance of `librus_apix.client.Client` used to make requests to the Librus platform.

    Returns:
        List[NotificationAmount]: A list of `NotificationAmount` objects representing the notifications found on the user's dashboard.
    """
    soup = no_access_check(BeautifulSoup(client.get(client.INDEX_URL).text, "lxml"))
    notifications = []
    circles = soup.select("div#graphic-menu > ul > li > a[class!='button counter']")
    for circle in circles:
        name = circle.text.replace("\n", "").strip()
        destination = circle.attrs.get("href", "/")
        amount = 0
        if (
            name == "Widok alternatywny"
            or "javascript" in destination
            or destination
            not in [
                "/ogloszenia",
                "/moje_zadania",
                "/wiadomosci",
                "/przegladaj_oceny/uczen",
                "/przegladaj_nb/uczen",
                "/terminarz",
            ]
        ):
            continue

        if isinstance(circle.parent, Tag):
            counter = circle.parent.select_one("a.button.counter")
            if isinstance(counter, Tag):
                try:
                    amount = int(counter.text)
                except ValueError:
                    pass

        notifications.append(NotificationAmount(name, destination, amount))

    return notifications


def _compare_hrefs(object_href: str, href_ids: List[str]):
    return object_href in href_ids


def _parse_recent_schedule_notification(
    schedule: List[RecentEvent], seen_ids: List[str] = []
):
    new_schedule = []
    for event in schedule:
        data_bytes = event.data.encode("utf-8")
        _id = md5(data_bytes).hexdigest()
        if _compare_hrefs(_id, seen_ids):
            continue
        seen_ids.append(_id)
        new_schedule.append(event)
    return new_schedule, seen_ids


def _parse_announcements_notification(
    announcements: List[Announcement], seen_ids: List[str] = []
):
    new_announcements = []
    for announcement in announcements:
        _id = announcement.title + announcement.date
        if _compare_hrefs(_id, seen_ids):
            break
        seen_ids.append(_id)
        new_announcements.append(announcement)
    return new_announcements, seen_ids


def _parse_homework_notification(homework: List[Homework], seen_ids: List[str] = []):
    new_homework = []
    for hw in homework:
        href = hw.href
        if _compare_hrefs(href, seen_ids):
            break
        seen_ids.append(href)
        new_homework.append(hw)
    return new_homework, seen_ids


def _parse_messages_notification(messages: List[Message], seen_ids: List[str] = []):
    new_messages = []
    new_ids = []
    for message in messages:
        href = message.href
        if _compare_hrefs(href, seen_ids):
            break
        if message.unread == False:
            continue
        new_ids.append(href)
        new_messages.append(message)
    if len(messages) > 0 and len(seen_ids) == 0:
        seen_ids.append(messages[0].href)
    else:
        seen_ids.extend(new_ids)
    return new_messages, seen_ids


def _parse_attendance_notification(
    attendance: List[List[Attendance]], seen_ids: List[str] = []
):
    new_attendance = []
    for semester in attendance:
        for semester_attendance in semester:
            href = semester_attendance.href
            if _compare_hrefs(href, seen_ids):
                continue
            seen_ids.append(href)
            new_attendance.append(semester_attendance)
    return new_attendance, seen_ids


def _parse_grades_notifications(
    grades: List[DefaultDict[str, List[Grade]]], seen_ids: List[str] = []
):
    new_grades = []
    for semester in grades:
        for subject_grades in semester.values():
            for grade in subject_grades:
                href = grade.href
                if _compare_hrefs(href, seen_ids):
                    continue
                new_grades.append(grade)
                seen_ids.append(href)
    return new_grades, seen_ids


def parse_basic_amount(
    client: Client, amount: NotificationAmount
) -> Tuple[List[Any], List[str]]:
    if amount.amount == 0 and amount.destination not in [
        "/ogloszenia",
        "/moje_zadania",
        "/wiadomosci",
    ]:
        return [], []
    match amount.destination:
        case "/przegladaj_oceny/uczen":
            grades, _averages, _descriptive = get_grades(client, "last_login")
            return _parse_grades_notifications(grades)
        case "/przegladaj_nb/uczen":
            attendance = get_attendance(client, "last_login")
            return _parse_attendance_notification(attendance)
        case "/wiadomosci":
            messages = get_received(client, 0)
            top_two_msgs = messages[:2]
            if len(top_two_msgs) == 0:
                return [], []
            else:
                return _parse_messages_notification(top_two_msgs)

        case "/ogloszenia":
            announcements = get_announcements(client)
            newest = announcements[: amount.amount]
            if len(newest) == 0:
                newest = [announcements[0]]
                _, ids = _parse_announcements_notification(newest)
                return [], ids
            else:
                return _parse_announcements_notification(newest)

        case "/terminarz":
            schedule = get_recently_added_schedule(client)
            return schedule, []
        case "/moje_zadania":
            today = datetime.now()
            hw_amount = -amount.amount
            if hw_amount == 0:
                hw_amount = -1
            homework = get_homework(
                client,
                (today - timedelta(days=7)).strftime("%Y-%m-%d"),
                today.strftime("%Y-%m-%d"),
            )[hw_amount:]
            if amount.amount == 0:
                _, ids = _parse_homework_notification(homework)
                return [], ids
            else:
                return _parse_homework_notification(homework)

        case _:
            return [], []


@dataclass
class NotificationData:
    """
    Represents data of various notifications.

    Attributes:
        grades (List[Grade]): A list of grade notifications.
        attendance (List[Attendance]): A list of attendance notifications.
        messages (List[Message]): A list of message notifications.
        announcements (List[Announcement]): A list of announcement notifications.
        schedule (List[RecentEvent]): A list of schedule notifications.
        homework (List[Homework]): A list of homework notifications.
    """

    grades: List[Grade]
    attendance: List[Attendance]
    messages: List[Message]
    announcements: List[Announcement]
    schedule: List[RecentEvent]
    homework: List[Homework]


@dataclass
class NotificationIds:
    """
    Represents the IDs (mostly .href) of various notifications to track seen notifications.

    Attributes:
        grades (List[str]): A list of grade notification IDs.
        attendance (List[str]): A list of attendance notification IDs.
        messages (List[str]): A list of message notification IDs.
        announcements (List[str]): A list of announcement notification IDs (title+data) concat.
        schedule (List[str]): A list of schedule notification IDs.
        homework (List[str]): A list of homework notification IDs.
    """

    grades: List[str]
    attendance: List[str]
    messages: List[str]
    announcements: List[str]
    schedule: List[str]
    homework: List[str]


def get_initial_notification_data(client: Client):
    """
    Fetches and parses the initial notification data and their IDs for a new token.
    ! Should only be ran once on every new Token. The notifications are stored inside Token and won't update.

    Args:
        client (Client): An instance of `librus_apix.client.Client`.

    Returns:
        Tuple[NotificationData, NotificationIds]: A tuple containing the initial notification data and their IDs.
    """
    amounts = get_new_token_notification_amounts(client)
    amounts = map(lambda amount: parse_basic_amount(client, amount), amounts)
    notify_data = []
    notify_ids = []
    for data, ids in amounts:
        notify_data.append(data)
        notify_ids.append(ids)

    if len(notify_data) != 6:
        raise ParseError("notification length doenst match expected 6")
    return NotificationData(*notify_data), NotificationIds(*notify_ids)


def get_new_notification_data(client: Client, seen_notifications: NotificationIds):
    """
    Fetches and parses new notification data and updates seen notification IDs based on given NotificationIds.

    Args:
        client (Client): An instance of `librus_apix.client.Client`.
        seen_notifications (NotificationIds): A `NotificationIds` object representing the seen notifications.

    Returns:
        Tuple[NotificationData, NotificationIds]: A tuple containing the new notification data and updated seen notification IDs.
    """
    grades, _, _ = get_grades(client, "last_login")
    attendance = get_attendance(client, "last_login")
    messages = get_received(client, 0)
    announcements = get_announcements(client)
    today = datetime.now()
    homework = get_homework(
        client,
        (today - timedelta(days=7)).strftime("%Y-%m-%d"),
        today.strftime("%Y-%m-%d"),
    )[::-1]

    schedule = get_recently_added_schedule(client)

    new_schedule, seen_events = _parse_recent_schedule_notification(
        schedule, seen_notifications.schedule
    )
    new_grades, seen_grades = _parse_grades_notifications(
        grades, seen_notifications.grades
    )
    new_attendance, seen_attendance = _parse_attendance_notification(
        attendance, seen_notifications.attendance
    )
    new_messages, seen_messages = _parse_messages_notification(
        messages, seen_notifications.messages
    )
    new_announcements, seen_announcements = _parse_announcements_notification(
        announcements, seen_notifications.announcements
    )
    new_homework, seen_homework = _parse_homework_notification(
        homework, seen_notifications.homework
    )

    return NotificationData(
        new_grades,
        new_attendance,
        new_messages,
        new_announcements,
        new_schedule,
        new_homework,
    ), NotificationIds(
        seen_grades,
        seen_attendance,
        seen_messages,
        seen_announcements,
        seen_events,
        seen_homework,
    )
