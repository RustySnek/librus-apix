from typing import Generator
from bs4 import BeautifulSoup
from get_token import get_token, Token
from urls import BASE_URL, HOMEWORK_URL
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

def homework_detail(token: Token, detail_url: str) -> dict[str, str]:
    h_desc = {}
    line = BeautifulSoup(token.get(HOMEWORK_URL + detail_url).text, "lxml").find("div", attrs={"class": "container-background"}).find_all("tr", attrs={"class": ["line0", "line1"]})
    if line is None:
        return {'error': 'Malformed token'}, 401
    for td in line:
        h_desc[td.find_all("td")[0].text.replace("\xa0", " ")] = td.find_all("td")[
            1
        ].text.replace("\xa0", " ")
    return h_desc, 200

def get_homework(token: Token, date_from: str, date_to: str) -> list[Homework]:
    hw = {'homework': []}
    soup = BeautifulSoup(
        token.post(
            BASE_URL + "/moje_zadania",
            data={"dataOd": date_from, "dataDo": date_to, "przedmiot": "-1", "status": "-1"},
        ).text,
        "lxml",
    ).find("table", attrs={"class": "decorated myHomeworkTable"})
    if soup is None:
        return {'error': 'Malformed token'}, 401
    lines = soup.find_all(
        "tr", attrs={"class": ["line0", "line1"]}
    )
    for line in lines:
        hw_list = [txt.text.replace("\n", "") for txt in line.find_all("td")]
        href = line.find("input").attrs["onclick"].split("'")[1].split('/')[3]
        h = Homework(
            hw_list[0],
            hw_list[1],
            hw_list[2],
            hw_list[3],
            str(hw_list[4] + " " + hw_list[5]),
            str(hw_list[6] + " " + str(hw_list[7])),
            href,
        )
        hw['homework'].append(h.__dict__)
    return hw, 200
