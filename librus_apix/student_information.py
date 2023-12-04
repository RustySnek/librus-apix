from bs4 import BeautifulSoup
from dataclasses import dataclass
from librus_apix.helpers import no_access_check
from librus_apix.urls import INFO_URL
from librus_apix.get_token import Token


@dataclass
class StudentInformation:
    name: str
    class_name: str
    number: int
    tutor: str
    school: dict
    lucky_number: int


def get_student_information(token: Token):
    soup = no_access_check(
        BeautifulSoup(
            token.get(INFO_URL).text,
            "lxml",
        )
    )
    lucky_number = soup.select_one("span.luckyNumber > b").text
    lines = soup.select_one("table.decorated.big.center > tbody").find_all(
        "tr", attrs={"class": ["line0", "line1"]}
    )[:5]
    name, class_name, number, tutor, school = [
        val.select_one("td").text.strip() for val in lines
    ]
    return StudentInformation(
        name,
        class_name,
        int(number),
        tutor,
        "\n".join([n.strip() for n in school.split("\n")]),
        int(lucky_number),
    )
