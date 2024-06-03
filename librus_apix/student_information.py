"""
This module provides functions for retrieving student information from the Librus system, parsing it, and formatting it into a structured representation.

Classes:
    - StudentInformation: Represents student information with attributes such as name, class name, student number, etc.

Functions:
    - get_student_information: Retrieves student information from Librus.

Usage:
    ```python
    from librus_apix.client import new_client

    # Create a new client instance
    client = new_client()
    client.get_token(username, password)

    # Fetch student information
    student_info = get_student_information(client)
    print(student_info.name)
    print(student_info.class_name)
    print(student_info.number)
    print(student_info.tutor)
    print(student_info.school)
    print(student_info.lucky_number)
    ```
"""

from typing import Union
from bs4 import BeautifulSoup
from dataclasses import dataclass
from librus_apix.exceptions import ParseError
from librus_apix.helpers import no_access_check
from librus_apix.client import Client


@dataclass
class StudentInformation:
    """
    Represents student information.

    Attributes:
        name (str): The name of the student.
        class_name (str): The class name of the student.
        number (int): The student number.
        tutor (str): The tutor of the student.
        school (str): The school of the student.
        lucky_number (Union[int, str]): The lucky number of the student, if available.
    """

    name: str
    class_name: str
    number: int
    tutor: str
    school: str
    lucky_number: Union[int, str]


def get_student_information(client: Client):
    """
    Retrieves student information from librus.

    Args:
        client (Client): The client object for making HTTP requests.

    Returns:
        StudentInformation: An object containing the student's information.

    Raises:
        ParseError: If there is an error while parsing or retrieving student information.
    """
    soup = no_access_check(
        BeautifulSoup(
            client.get(client.INFO_URL).text,
            "lxml",
        )
    )
    try:
        lucky_number = soup.select_one("span.luckyNumber > b")
        if lucky_number is None:
            lucky_number = "?"
        else:
            lucky_number = int(lucky_number.text)
    except ValueError:
        lucky_number = "?"

    table = soup.select_one("table.decorated.big.center > tbody")
    if table is None:
        raise ParseError("Error while parsing student information table")
    lines = table.find_all("tr", attrs={"class": ["line0", "line1"]})[:5]
    data = [val.select_one("td").text.strip() for val in lines]
    if len(data) < 5:
        raise ParseError("Error while retrieving student information")
    name, class_name, number, tutor, school = data[:5]
    return StudentInformation(
        name,
        class_name,
        int(number),
        tutor,
        "\n".join([n.strip() for n in school.split("\n")]),
        lucky_number,
    )
