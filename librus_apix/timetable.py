from get_token import get_token
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class Period:
    subject: str
    teacher_and_classroom: str
    date: str
    date_from: str
    date_to: str
    weekday: str
    info: dict[str, str]

def get_timetable(token, monday_date: datetime):
    timetable: defaultdict[str, list[Period]] = defaultdict(list)
    sunday = monday_date + timedelta(days=6)
    week = f"{monday_date.strftime('%Y-%m-%d')}_{sunday.strftime('%Y-%m-%d')}"
    post = token.post("https://synergia.librus.pl/przegladaj_plan_lekcji", data = {"tydzien": week})
    soup = BeautifulSoup(post.text, 'lxml')
    periods = soup.select('table.decorated.plan-lekcji > tr.line1')
    if len(periods) < 1:
        return {'error': 'Malformed token'}, 401
    recess = soup.select('table.decorated.plan-lekcji > tr.line0')
    last_period = periods[-1].select_one('td.center').text
    for weekday in range(7):
        for period in range(int(last_period)):
            lesson = periods[period].select('td[id="timetableEntryBox"][class="line1"]')[weekday]
            tooltip = lesson.select_one('div.center.plan-lekcji-info')
            a_href = lesson.select_one('a')
            info = {}
            if tooltip is not None:
                if a_href is None:
                    info[tooltip.text.strip()] = ""
                else:
                    info[tooltip.text.strip()] = (
                    a_href
                    .attrs['title']
                    .replace('<br>', " ")
                    .replace("<b>", '')
                    .replace('</b>', "")
                    .replace(u'\xa0', " ")
                    )

            date, date_from, date_to = [val for key,val in lesson.attrs.items() if key.startswith("data")]
            lesson = lesson.select_one('div.text')
            try:
                subject, teacher_and_classroom = (
                    lesson.text
                    .replace(u'\xa0', " ")
                    .replace('\n', "")
                    .replace('&nbsp', '')
                    .split('-')
                )
            except:
                subject = ""
                teacher_and_classroom = ""

            weekday_str = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
            p = Period(subject, teacher_and_classroom, date, date_from, date_to, weekday_str, info)
            timetable[weekday_str].append(p.__dict__)
    return timetable, 200