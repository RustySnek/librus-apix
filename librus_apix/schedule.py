"""
This module provides functions for retrieving schedule information from the Librus site, parsing it, and formatting it into a structured representation.

Classes:
    - Event: Represents an event in the schedule with various attributes like title, subject, day, etc.

Functions:
    - schedule_detail: Fetches detailed schedule information for a specific prefix and detail URL suffix.
    - get_schedule: Fetches the schedule for a specific month and year.

Usage:
    ```python
    from librus_apix.client import new_client

    # Create a new client instance
    client = new_client()
    client.get_token(username, password)


    # Fetch the schedule for a specific month and year
    month = "01"
    year = "2024"
    include_empty = True
    monthly_schedule = get_schedule(client, month, year, include_empty)

    # Fetch detailed schedule information
    day_one = monthly_schedule[1].href
    prefix, suffix = day_one.split("/")
    detailed_schedule = schedule_detail(client, prefix, detail_url)
    ```
"""

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Dict, List, Union

from bs4 import BeautifulSoup, NavigableString, Tag

from librus_apix.client import Client
from librus_apix.exceptions import ParseError
from librus_apix.helpers import no_access_check


@dataclass
class Event:
    """
    Represents an event in the schedule.

    Attributes:
        title (str): The title of the event.
        subject (str): The subject of the event.
        data (dict): Additional data associated with the event.
        day (str): The day on which the event occurs.
        number (Union[int, str]): The number associated with the event.
        hour (str): The hour at which the event occurs.
        href (str): 'prefix'/'suffix' joined with a slash (this should be reworked...).
    """

    title: str
    subject: str
    data: dict
    day: str
    number: Union[int, str]
    hour: str
    href: str


def schedule_detail(client: Client, prefix: str, detail_url: str) -> Dict[str, str]:
    """
    Fetches the detailed schedule information for a specific prefix and detail URL suffix.

    Args:
        client (Client): The client object for making HTTP requests.
        prefix (str): The prefix of the schedule URL.
        detail_url (str): The detail URL of the schedule.

    Returns:
        Dict[str, str]: A dictionary containing schedule details.
    """
    schedule = {}
    div = no_access_check(
        BeautifulSoup(
            client.get(client.SCHEDULE_URL + prefix + "/" + detail_url).text, "lxml"
        )
    ).find("div", attrs={"class": "container-background"})

    if div is None or isinstance(div, NavigableString):
        raise ParseError("Error in parsing schedule details.")
    tr: List[Tag] = div.find_all("tr", attrs={"class": ["line0", "line1"]})
    for s in tr:
        th = s.find("th")
        td = s.find("td")
        if td is None or th is None:
            continue
        schedule[th.text.strip()] = td.text.strip()
    return schedule


def _parse_title_into_pairs(title: str) -> Dict[str, str]:
    additional_data = {}
    pairs = [pair.split(":", 1) for pair in title.split("<br />")]
    for pair in pairs:
        if len(pair) != 2:
            additional_data[pair[0].strip()] = "unknown"
            continue
        key, val = pair
        additional_data[key.strip()] = val.strip()

    return additional_data


def get_schedule(
    client: Client, month: str, year: str, include_empty: bool = False
) -> DefaultDict[int, List[Event]]:
    """
    Fetches the schedule for a specific month and year.

    Args:
        client (Client): The client object for making HTTP requests.
        month (str): The month for which the schedule is requested.
        year (str): The year for which the schedule is requested.
        include_empty (bool, optional): Flag to include empty schedules. Defaults to False.

    Returns:
        DefaultDict[int, List[Event]]: A dictionary containing the schedule for each day of the month.
    """
    schedule = defaultdict(list)
    soup = no_access_check(
        BeautifulSoup(
            client.post(client.SCHEDULE_URL, data={"rok": year, "miesiac": month}).text,
            "lxml",
        )
    )
    days = soup.find_all("div", attrs={"class": "kalendarz-dzien"})
    if len(days) < 1:
        raise ParseError("Error in parsing days of the schedule.")
    for day in days:
        try:
            d = int(day.find("div", attrs={"class": "kalendarz-numer-dnia"}).text)
        except:
            raise ParseError("Error while parsing day number")
        if include_empty == True:
            schedule[d] = []
        tr: List[Tag] = day.find_all("tr")
        for event in tr:
            td = event.find("td")
            if td is None or isinstance(td, NavigableString):
                continue
            title = td.attrs.get("title", "Nauczyciel: unknown<br />Opis: unknown")
            additional_data = _parse_title_into_pairs(title)
            subject = "unspecified"
            span = td.find("span")
            if span is not None:
                subject = span.text
                span.extract()

            delimeter = "###"
            for line in td.select("br"):
                line.replaceWith(delimeter)
            data = (
                td.text.replace("\xa0", " ")
                .replace(", ", "")
                .replace("\n", "")
                .strip()
                .split(delimeter)
            )
            if subject == "unspecified":
                subject = data[0]
            if len(data) >= 2:
                title = data[1]
            else:
                title = data[0]

            number = "unknown"
            hour = "unknown"
            number_td = event.find("td")
            if number_td is None or isinstance(number_td, NavigableString):
                raise ParseError("Error while parsing td_number schedule.")
            try:
                number = int(
                    re.findall(r": ?[0-99]?[0-99]", number_td.text)[0].replace(": ", "")
                )
            except ValueError:
                hour = re.findall(r" ?[0-2]?[0-9]:?[0-5]?[0-9]", number_td.text)[0]
            except IndexError:
                pass
            onclick = number_td.attrs.get("onclick", "'")
            href = onclick.split("'")[1].split("/")
            if len(href) >= 2:
                href = "/".join(href[2:])
            else:
                href = ""

            event = Event(title, subject, additional_data, str(d), number, hour, href)
            schedule[d].append(event)
    return schedule


@dataclass
class RecentEvent:
    """
    The events inside recent_schedule differ a little bit
    the .data should contain event name, date from to and duration
    I might be able to extract into separate values if I get html
    """

    date_added: str
    type: str
    data: str


def _sanitize_data(data: str) -> str:
    return (
        data.replace("&nbsp;", " ")
        .replace("<br/>", "<br>")
        .replace("<br>", "\n")
        .strip()
    )


def get_recently_added_schedule(client: Client) -> List[RecentEvent]:
    """
    Events can be viewed only once here, any subsequent call won't have same events
    Made blindly based on a screenshot, still untested...
    """
    events = []
    soup = no_access_check(
        BeautifulSoup(
            client.get(client.RECENT_SCHEDULE_URL).text,
            "lxml",
        )
    )
    bg = soup.select_one("div.container-background")
    if bg is None:
        raise ParseError("Unable to locate recent schedule container-background")
    table = soup.select_one("table")
    if table is None:
        return []
    rows = table.select("tr")
    for row in rows:
        tds = row.select("td")
        if len(tds) != 4:
            continue
        _, date_added, _type, data = tds
        data = _sanitize_data(data.text)
        # unsure about that so we'll check
        if "czas dodania" in date_added and "rodzaj zdarzenia" in _type:
            continue
        event = RecentEvent(date_added.text.strip(), _type.text.strip(), data)
        events.append(event)
    return events
