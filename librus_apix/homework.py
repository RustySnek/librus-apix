"""
This module provides functions for retrieving homework assignments from the Librus site, parsing them, and fetching detailed information about specific assignments.

Classes:
    - Homework: Represents a homework assignment with detailed information such as lesson, teacher, subject, etc.

Functions:
    - homework_detail: Retrieves detailed information about a specific homework assignment.
    - get_homework: Retrieves homework assignments within a specified date range.

Usage:
```python
from librus_apix.client import new_client

# Create a new client instance
client = new_client()
client.get_token(username, password)

# Retrieve homework assignments within a specified date range
date_from = "YYYY-MM-DD"
date_to = "YYYY-MM-DD"
homework_assignments = get_homework(client, date_from, date_to)

# Retrieve detailed information about a specific homework assignment
for homework in homework_assignments:
    homework_details = homework_detail(client, homework.href)
```
"""

from typing import List, Dict
from bs4 import BeautifulSoup, NavigableString
from librus_apix.client import Client
from librus_apix.helpers import no_access_check
from librus_apix.exceptions import ParseError
from dataclasses import dataclass


@dataclass
class Homework:
    """
    Represents a homework assignment with detailed information.

    Attributes:
        lesson (str): The lesson or topic associated with the homework.
        teacher (str): The name of the teacher who assigned the homework.
        subject (str): The subject for which the homework is assigned.
        category (str): The category or type of homework (e.g., assignment, project).
        task_date (str): The date when the homework was assigned.
        completion_date (str): The date by which the homework needs to be completed.
        href (str): A URL suffix or link associated with the homework for more details.
    """

    lesson: str
    teacher: str
    subject: str
    category: str
    task_date: str
    completion_date: str
    href: str


def _sanitize_onclick_href(onclick: str) -> str:
    href = onclick.split("'")
    if len(href) < 2:
        return ""

    href = href[1].split("/")
    if len(href) < 4:
        return ""
    return href[3]


def homework_detail(client: Client, detail_url: str) -> Dict[str, str]:
    """
    Fetches and parses detailed information about a specific homework assignment.

    Args:
        client (Client): The client object used to interact with the server.
        detail_url (str): The URL suffix to fetch the detailed homework information.

    Returns:
        Dict[str, str]: A dictionary containing detailed homework information where the keys are detail labels
                        and the values are the corresponding detail values.

    Raises:
        ParseError: If there is an error in parsing the homework details.
    """
    h_desc = {}
    soup = no_access_check(
        BeautifulSoup(client.get(client.HOMEWORK_DETAILS_URL + detail_url).text, "lxml")
    )
    div = soup.find("div", attrs={"class": "container-background"})
    if div is None or isinstance(div, NavigableString):
        raise ParseError("Error in parsing Homework details.")
    line = div.find_all("tr", attrs={"class": ["line0", "line1"]})
    for td in line:
        pair = td.find_all("td")
        if len(pair) < 2:
            continue
        h_desc[pair[0].text.replace("\xa0", " ")] = pair[1].text.replace("\xa0", " ")
    return h_desc


def get_homework(client: Client, date_from: str, date_to: str) -> List[Homework]:
    """
    Fetches and parses the list of homework assignments within a specified date range.

    Args:
        client (Client): The client object used to interact with the server.
        date_from (str): The start date for fetching homework assignments (format: 'YYYY-MM-DD').
        date_to (str): The end date for fetching homework assignments (format: 'YYYY-MM-DD').

    Returns:
        List[Homework]: A list of Homework objects representing the homework assignments within the specified date range.

    Raises:
        ParseError: If there is an error in parsing the homework assignments.
    """
    soup_base = no_access_check(
        BeautifulSoup(
            client.post(
                client.HOMEWORK_URL,
                data={
                    "dataOd": date_from,
                    "dataDo": date_to,
                    "przedmiot": "-1",
                    "status": "-1",
                },
            ).text,
            "lxml",
        )
    )
    soup = soup_base.find("table", attrs={"class": "decorated myHomeworkTable"})
    if soup is None or isinstance(soup, NavigableString):
        # no proper content found - error or no data
        soup = soup_base.find("p", attrs={"class": "msgEmptyTable"})
        if soup is not None:
            # empty table found - return empty list
            return []
        # parsing error
        raise ParseError("Error in parsing homework.")
    hw = []
    lines = soup.find_all("tr", attrs={"class": ["line0", "line1"]})
    for line in lines:
        hw_list = [txt.text.replace("\n", "") for txt in line.find_all("td")]
        if len(hw_list) < 8:
            raise ParseError(
                "Error while parsing homework data. homework has less than 8 elements"
            )
        href = line.find("input")
        onclick = href.attrs.get("onclick", "") if line is not None else ""
        href = _sanitize_onclick_href(onclick)
        h = Homework(
            hw_list[0],
            hw_list[1],
            hw_list[2],
            hw_list[3],
            str(hw_list[4] + " " + hw_list[5]),
            str(hw_list[6] + " " + hw_list[7]),
            href,
        )
        hw.append(h)
    return hw
