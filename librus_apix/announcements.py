"""
This module provides functions for retrieving announcements from the Librus site and parsing them into Announcement objects.

Classes:
    - Announcement: Represents an announcement with attributes for title, author, description, and date.

Functions:
    - get_announcements: Retrieves a list of announcements from the Librus API using a Client object.

Usage:
```python
from librus_apix.client import new_client

# Create a new client instance
client = new_client()
client.get_token(username, password)

# Retrieve announcements
announcements = get_announcements(client)
```
"""

from dataclasses import dataclass
from typing import List

from bs4 import BeautifulSoup

from librus_apix.client import Client
from librus_apix.exceptions import ParseError
from librus_apix.helpers import no_access_check


@dataclass
class Announcement:
    """
    Represents an announcement.

    Attributes:
        title (str): The title of the announcement.
        author (str): The author of the announcement.
        description (str): The description of the announcement.
        date (str): The date of the announcement.
    """

    title: str = ""
    author: str = ""
    description: str = ""
    date: str = ""


def get_announcements(client: Client) -> List[Announcement]:
    """
    Retrieves a list of announcements from the client.

    Args:
        client (Client): The client object used to make the request.

    Returns:
        List[Announcement]: A list of Announcement objects representing the retrieved announcements.

    Raises:
        ParseError: If there is an error parsing the announcements.
    """
    soup = no_access_check(
        BeautifulSoup(client.get(client.ANNOUNCEMENTS_URL).text, "lxml")
    )
    if soup.select_one("div.container.border-red.resizeable.center > div > p"):
        return []
    announcements = []
    announcement_tables = soup.select("table.decorated.big.center.printable.margin-top")
    if len(announcement_tables) < 1:
        raise ParseError("Error in parsing announcements")
    for table in announcement_tables:
        title = table.select_one("thead > tr > td")
        title = title.text if title is not None else ""

        data = [
            (
                line.select_one("td").text.strip()
                if line.select_one("td") is not None
                else ""
            )
            for line in table.find_all("tr", attrs={"class": ["line0", "line1"]})
        ]
        if len(data) != 3:
            raise ParseError(f"Expected 3 items in Announcement data, got {len(data)}")
        author, date, desc = data
        a = Announcement(title, author, desc, date)
        announcements.append(a)
    return announcements
