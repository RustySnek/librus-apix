from typing import List, Dict
from bs4 import BeautifulSoup
from librus_apix.get_token import Token
from librus_apix.helpers import no_access_check
from librus_apix.exceptions import ParseError
from dataclasses import dataclass


@dataclass
class Attendance:
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


def get_detail(token: Token, detail_url: str) -> Dict[str, str]:
    details = {}
    div = no_access_check(
        BeautifulSoup(token.get(token.ATTENDANCE_DETAILS_URL + detail_url).text, "lxml")
    ).find("div", attrs={"class": "container-background"})
    line = div.find_all("tr", attrs={"class": ["line0", "line1"]})
    if len(line) < 1:
        raise ParseError("Error in parsing attendance.")
    for l in line:
        if not l.find("th"):
            continue
        details[l.find("th").text] = l.find("td").text
    return details

def get_gateway_attendance(token: Token):
    # The gateway api seems to be only updated every 3 hours
    # The api.librus.pl seems to require a private key to access
    types = {
            "1": {"short": "nb" ,"name": "Nieobecność"},
            "2": {"short": "sp" ,"name": "Spóźnienie"},
            "3": {"short": "u" ,"name": "Nieobecność uspr."},
            "4": {"short": "zw" ,"name": "Zwolnienie"},
            "100": {"short": "ob" ,"name": "Obecność"},
            "1266": {"short": "wy" ,"name": "Wycieczka"},
            "2022": {"short": "k" ,"name": "Konkurs szkolny"},
            "2829": {"short": "sz" ,"name": "Szkolenie"},
            }
    if token.oauth == "":
        token.refresh_oauth()
    token.cookies["oauth_token"] = token.oauth
    response = token.get(token.GATEWAY_API_ATTENDANCE)

    attendances = response.json()["Attendances"]


    return [
            (tuple(
                types[
                    str(a["Type"]["Id"])].values()),
            a["LessonNo"],
            a["Semester"]
            ) for a in attendances]

def get_attendance_frequency(token: Token):
    attendance = get_gateway_attendance(token)
    first_semester = [a for a in attendance if a[2] == 1]
    second_semester = [a for a in attendance if a[2] == 2]
    f_attended = len([a for a in first_semester if a[0][0] == "ob"])
    s_attended = len([a for a in second_semester if a[0][0] == "ob"])
    f_freq = f_attended / len(first_semester) if len(second_semester) != 0 else 1
    s_freq = s_attended / len(second_semester) if len(second_semester) != 0 else 1
    overall_freq = len([a for a in attendance if a[0][0] == "ob"]) / len(attendance) if len(attendance) != 0 else 1
    return f_freq, s_freq, overall_freq
    # ADD Lesson frequency

def get_attendance(token: Token, sort_by: str = "all") -> List[List[Attendance]]:
    SORT = {
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
            token.post(token.ATTENDANCE_URL, data=SORT[sort_by]).text,
            "lxml",
        )
    )
    table = soup.find("table", attrs={"class": "center big decorated"})
    if table is None:
        raise ParseError("Error parsing attendance.")
    days = table.find_all("tr", attrs={"class": ["line0", "line1"]})
    att = [[], []]
    semester = -1
    for day in days:
        if day.find("td", attrs={"class": "center bolded"}):
            semester += 1
        date = day.find("td", attrs={"class": None})
        attendance = day.find_all("td", attrs={"class": "center"})
        for attend in attendance:
            at = attend.find_all("a")
            for single in at:
                if not single:
                    continue
                attributes = {
                    i.split(": ")[0].strip(): i.split(": ")[1].strip()
                    for i in single.attrs["title"]
                    .replace("</b>", "<br>")
                    .replace("<br/>", "")
                    .strip()
                    .split("<br>")
                }
                date = attributes["Data"].split(" ")[0]
                _type = attributes["Rodzaj"]
                school_subject = attributes["Lekcja"]
                topic = attributes.get("Temat zajęć")  # optional
                period = int(attributes["Godzina lekcyjna"])
                excursion = True if attributes["Czy wycieczka"] == "Tak" else False
                teacher = attributes["Nauczyciel"]

                href = (
                    single.attrs["onclick"]
                    .replace("otworz_w_nowym_oknie(", "")
                    .split(",")[0]
                    .replace("'", "")
                    .split("/")[3]
                )
                a = Attendance(
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
                att[semester].append(a)
    return list(reversed(att))
