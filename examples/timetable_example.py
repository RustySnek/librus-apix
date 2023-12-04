from datetime import datetime
from librus_apix.timetable import get_timetable
from librus_apix.get_token import get_token

username = "USERNAME"
password = "PASSWORD"
token = get_token(username, password)

monday_date = "2023-04-03"
monday_datetime = datetime.strptime(monday_date, "%Y-%m-%d")
timetable = get_timetable(token, monday_datetime)

"""
The monday_datetime has to be Monday date else it will raise and error.

timetable(token, monday_datetime) -> dict[str, list[Period]]

Structure of Period class:
    class Period:
        subject: str
        teacher_and_classroom: str
        date: str
        date_from: str
        date_to: str
        weekday: str
        info: dict[str, str]
        number: int
"""

# Printing out the full timetable starting from the Monday datetime provided.
for weekday in timetable:
    print()
    print(weekday)
    for period in timetable[weekday]:
        print(period.number, period.subject, period.teacher_and_classroom)
