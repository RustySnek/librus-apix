"""
This module provides functionality to interact with the Librus API and extract notifications from the user's dashboard.

It defines a `Notification` dataclass to encapsulate notification details and includes a function, `get_notifications`,
to fetch and parse notifications from the user's dashboard.

Classes:
    - Notification: Represents a notification with a destination and an amount.

Functions:
    - _extract_name_from_id(id: str) -> str: Extracts a name or identifier from a given ID string.
    - get_notifications(client: Client) -> List[Notification]: Fetches and parses notifications from the user's dashboard on the Librus platform.
"""

from dataclasses import dataclass
from typing import List
from bs4 import BeautifulSoup, Tag
from librus_apix.client import Client
from librus_apix.helpers import no_access_check


@dataclass
class Notification:
    """
    Represents a notification with a destination identifier name and an amount.

    Attributes:
        destination (str): The identifier extracted from the id like 'ogloszenia', 'wiadomosci'.
        amount (int): The count of notifications for the given destination.
    """

    destination: str
    amount: int


def _extract_name_from_id(id: str) -> str:
    split = id.split("-", 1)
    if len(split) == 0:
        return ""
    return split[-1]


def get_notifications(client: Client) -> List[Notification]:
    """
    Fetches and parses notifications from the user's dashboard on the Librus platform.

    Args:
        client (Client): An instance of `librus_apix.client.Client` used to make requests to the Librus platform.

    Returns:
        List[Notification]: A list of `Notification` objects representing the notifications found on the user's dashboard.
    """
    soup = no_access_check(BeautifulSoup(client.get(client.INDEX_URL).text, "lxml"))
    notifications = []
    buttons = soup.select("li > a.button.counter")
    for button in buttons:
        prev_anchor = button.find_previous_sibling()
        destination = ""
        if isinstance(prev_anchor, Tag):
            id = prev_anchor.attrs.get("id", "")
            destination = _extract_name_from_id(id)
        try:
            amount = int(button.text)
        except ValueError:
            amount = 0
        notifications.append(Notification(destination, amount))

    return notifications
