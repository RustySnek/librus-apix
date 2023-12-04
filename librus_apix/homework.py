from typing import Generator, List, Dict
from bs4 import BeautifulSoup
from librus_apix.get_token import get_token, Token
from librus_apix.helpers import no_access_check
from librus_apix.urls import BASE_URL, HOMEWORK_URL
from librus_apix.exceptions import TokenError, ParseError
from dataclasses import dataclass


@dataclass
class Homework:
    lesson: str
    teacher: str
    subject: str
    category: str
    task_date: str
    completion_date: str
    href: str


def homework_detail(token: Token, detail_url: str) -> Dict[str, str]:
    h_desc = {}
    soup = no_access_check(
        BeautifulSoup(token.get(HOMEWORK_URL + detail_url).text, "lxml")
    )
    div = soup.find("div", attrs={"class": "container-background"})
    if div is None:
        raise ParseError("Error in parsing Homework details.")
    line = div.find_all("tr", attrs={"class": ["line0", "line1"]})
    for td in line:
        h_desc[td.find_all("td")[0].text.replace("\xa0", " ")] = td.find_all("td")[
            1
        ].text.replace("\xa0", " ")
    return h_desc


def get_homework(token: Token, date_from: str, date_to: str) -> List[Homework]:
    soup_base = no_access_check(
        BeautifulSoup(
            token.post(
                BASE_URL + "/moje_zadania",
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
    if soup is None:
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
        href = line.find("input").attrs["onclick"].split("'")[1].split("/")[3]
        h = Homework(
            hw_list[0],
            hw_list[1],
            hw_list[2],
            hw_list[3],
            str(hw_list[4] + " " + hw_list[5]),
            str(hw_list[6] + " " + str(hw_list[7])),
            href,
        )
        hw.append(h)
    return hw
