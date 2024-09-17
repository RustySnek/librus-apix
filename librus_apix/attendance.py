"""
This module provides functions for retrieving attendance records from the Librus site, parsing them, and calculating attendance frequency.

Classes:
    - Attendance: Represents an attendance record with various attributes such as type, date, teacher, etc.

Functions:
    - get_detail: Retrieves attendance details from a specific URL suffix.
    - get_gateway_attendance: Retrieves attendance data from the Librus gateway API.
    - get_attendance_frequency: Calculates attendance frequency for each semester and overall.
    - get_attendance: Retrieves attendance records from Librus based on specified sorting criteria.

Usage:
```python
from librus_apix.client import new_client

# Create a new client instance
client = new_client()
client.get_token(username, password)

# Retrieve attendance details
detail_url = "example_detail_url"
attendance_details = get_detail(client, detail_url)

# Retrieve attendance data from the gateway API
gateway_attendance = get_gateway_attendance(client)

# Calculate attendance frequency
first_sem_freq, second_sem_freq, overall_freq = get_attendance_frequency(client)

# Retrieve attendance records sorted by a specific criteria
attendance_records = get_attendance(client, sort_by="all")
```
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

from bs4 import BeautifulSoup, NavigableString, Tag

from librus_apix.client import Client
from librus_apix.exceptions import ArgumentError, ParseError
from librus_apix.helpers import no_access_check


@dataclass
class Attendance:
    """
    Represents an attendance record.

    Attributes:
        symbol (str): The symbol representing the attendance record.
        href (str): The URL associated with the attendance record.
        semester (int): The semester number to which the attendance record belongs.
        date (str): The date of the attendance record.
        type (str): The type of attendance (e.g., absence, presence).
        teacher (str): The name of the teacher associated with the attendance record.
        period (int): The period or hour of the attendance record.
        excursion (bool): Indicates if the attendance record is related to an excursion.
        topic (str): The topic or subject of the attendance record.
        subject (str): The school subject associated with the attendance record.
    """

    symbol: str
    href: str
    semester: int
    date: str
    type: str
    teacher: str
    period: int
    excursion: bool
    topic: str
    subject: str


def get_detail(client: Client, detail_url: str) -> Dict[str, str]:
    """
    Retrieves attendance details from the specified detail URL suffix.

    Args:
        client (Client): The client object used to make the request.
        detail_url (str): The URL for fetching the attendance details.

    Returns:
        Dict[str, str]: A dictionary containing the attendance details.

    Raises:
        ParseError: If there is an error parsing the attendance details.
    """
    details = {}
    div = no_access_check(
        BeautifulSoup(
            client.get(client.ATTENDANCE_DETAILS_URL + detail_url).text, "lxml"
        )
    ).find("div", attrs={"class": "container-background"})
    if div is None or isinstance(div, NavigableString):
        raise ParseError("Error in parsing attendance details")
    line = div.find_all("tr", attrs={"class": ["line0", "line1"]})
    if len(line) < 1:
        raise ParseError("Error in parsing attendance details (Lines are empty).")
    for l in line:
        th = l.find("th")
        td = l.find("td")
        if th is None or td is None:
            continue
        details[l.find("th").text] = l.find("td").text
    return details


def get_gateway_attendance(client: Client) -> List[Tuple[Tuple[str, str], str, str]]:
    """
    Retrieves attendance data from the gateway API.

    The gateway API data is typically updated every 3 hours.
    Accessing api.librus.pl requires a private key.

    Requires:
        oauth token to be refreshed with client.refresh_oauth()

    Args:
        client (Client): The client object used to make the request.

    Returns:
        List[Tuple[Tuple[str, str], str, str]]: A list of tuples containing attendance data.
            Each tuple contains three elements:
            1. Tuple containing type abbreviation and type name.
            2. Lesson number.
            3. Semester.

    Raises:
        ValueError: If the OAuth token is missing.
        AuthorizationError: If there is an authorization error while accessing the API.
    """
    types = {
        "1": {"short": "nb", "name": "Nieobecność"},
        "2": {"short": "sp", "name": "Spóźnienie"},
        "3": {"short": "u", "name": "Nieobecność uspr."},
        "4": {"short": "zw", "name": "Zwolnienie"},
        "100": {"short": "ob", "name": "Obecność"},
        "1266": {"short": "wy", "name": "Wycieczka"},
        "2022": {"short": "k", "name": "Konkurs szkolny"},
        "2829": {"short": "sz", "name": "Szkolenie"},
    }
    oauth = client.token.oauth
    if oauth == "":
        oauth = client.refresh_oauth()
    client.cookies["oauth_token"] = oauth
    response = client.get(client.GATEWAY_API_ATTENDANCE)

    attendances = response.json()["Attendances"]
    _attendance = []
    for a in attendances:
        type_id = a["Type"]["Id"]
        type_data = tuple(types[str(type_id)].values())
        lesson_number = a["LessonNo"]
        semester = a["Semester"]

        _attendance.append((type_data, lesson_number, semester))

    return _attendance


def get_attendance_frequency(client: Client) -> Tuple[float, float, float]:
    """
    Calculates the attendance frequency for each semester and overall.

    Args:
        client (Client): The client object used to retrieve attendance data.

    Returns:
        Tuple[float, float, float]: A tuple containing the attendance frequencies for the first semester, second semester, and overall.
            Each frequency is a float value between 0 and 1, representing the ratio of attended lessons to total lessons.

    Raises:
        ValueError: If there is an error retrieving attendance data.
    """
    attendance = get_gateway_attendance(client)
    first_semester = [a for a in attendance if a[2] == 1]
    second_semester = [a for a in attendance if a[2] == 2]
    f_attended = len([a for a in first_semester if a[0][0] in ["wy", "ob", "sp"]])
    s_attended = len([a for a in second_semester if a[0][0] in ["wy", "ob", "sp"]])
    f_freq = f_attended / len(first_semester) if len(second_semester) != 0 else 1
    s_freq = s_attended / len(second_semester) if len(second_semester) != 0 else 1
    overall_freq = (
        len([a for a in attendance if a[0][0] in ["wy", "ob", "sp"]]) / len(attendance)
        if len(attendance) != 0
        else 1
    )
    return f_freq, s_freq, overall_freq
    # ADD Lesson frequency


def _extract_title_pairs(title: str):
    sanitize_title = (
        title.replace("</b>", "<br>").replace("<br/>", "").strip().split("<br>")
    )

    return [pair.split(":", 1) for pair in sanitize_title]


def _sanitize_pairs(pairs: List[List[str]]) -> Dict[str, str]:
    sanitized_pairs = {}
    for pair in pairs:
        if len(pair) != 2:
            sanitized_pairs[pair[0].strip()] = "unknown"
            continue
        key, val = pair
        sanitized_pairs[key.strip()] = val.strip()
    return sanitized_pairs


def _sanitize_onclick_href(onclick: str):
    href = (
        onclick.replace("otworz_w_nowym_oknie(", "")
        .split(",")[0]
        .replace("'", "")
        .split("/")
    )
    if len(href) < 4:
        return ""
    return href[3]


def _create_attendance(single: Tag, semester: int):
    """
    Creates an Attendance object from a single attendance record.

    Args:
        single (Tag): The BeautifulSoup Tag representing a single attendance record.
        semester (int): The semester number to which the attendance record belongs.

    Returns:
        Attendance: An Attendance object representing the parsed attendance record.

    Raises:
        ParseError: If there is an error parsing the attendance record.
    """
    if single.attrs.get("title") is None:
        raise ParseError("Absence anchor title is None")
    pairs = _extract_title_pairs(single.attrs["title"])
    attributes = _sanitize_pairs(pairs)

    date = attributes.get("Data", "").split(" ")[0]
    _type = attributes.get("Rodzaj", "")
    school_subject = attributes.get("Lekcja", "")
    topic = attributes.get("Temat zajęć", "")
    period = int(attributes.get("Godzina lekcyjna", "0"))
    excursion = True if attributes.get("Czy wycieczka", "") == "Tak" else False
    teacher = attributes.get("Nauczyciel", "")

    href = _sanitize_onclick_href(single.attrs.get("onclick", ""))

    return Attendance(
        single.text,
        href,
        semester,
        date,
        _type,
        teacher,
        period,
        excursion,
        topic,
        school_subject,
    )


def get_attendance(client: Client, sort_by: str = "all") -> List[List[Attendance]]:
    """
    Retrieves attendance records from librus.

    Args:
        client (Client): The client object used to fetch attendance data.
        sort_by (str, optional): The sorting criteria for attendance records.
            It can be one of the following values:
            - "all": Sort by all attendance records.
            - "week": Sort by attendance records for the current week.
            - "last_login": Sort by attendance records since the last login.
            Defaults to "all".

    Returns:
        List[List[Attendance]]: A list containing attendance records grouped by semester.
            Each inner list represents attendance records for a specific semester.

    Raises:
        ArgumentError: If an invalid value is provided for the sort_by parameter.
        ParseError: If there is an error parsing the attendance data.
    """
    SORT: Dict[str, Dict[str, str]] = {
        "all": {"zmiany_logowanie_wszystkie": ""},
        "week": {"zmiany_logowanie_tydzien": "zmiany_logowanie_tydzien"},
        "last_login": {"zmiany_logowanie": "zmiany_logowanie"},
    }
    if sort_by not in SORT.keys():
        raise ArgumentError(
            "Wrong value for sort_by it can be either all, week or last_login"
        )

    soup = no_access_check(
        BeautifulSoup(
            client.post(client.ATTENDANCE_URL, data=SORT[sort_by]).text,
            "lxml",
        )
    )
    table = soup.find("table", attrs={"class": "center big decorated"})
    if table is None or isinstance(table, NavigableString):
        raise ParseError("Error parsing attendance (table).")

    days = table.find_all("tr", attrs={"class": ["line0", "line1"]})
    attendance_semesters = [[] for _ in range(2)]  # Two semesters
    semester = -1
    for day in days:
        if day.find("td", attrs={"class": "center bolded"}):
            # marker to increment semester
            semester += 1
        attendance = day.find_all("td", attrs={"class": "center"})
        for absence in attendance:
            a_elem: List[Tag] = absence.find_all("a")
            for single in a_elem:
                attendance_semesters[semester].append(
                    _create_attendance(single, semester)
                )
    match semester:
        case 0:
            return list(attendance_semesters)
        case 1:
            return list(reversed(attendance_semesters))
        case _:
            raise ParseError("Couldn't find attendance semester")
