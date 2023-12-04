from librus_apix.attendance import get_attendance
from librus_apix.get_token import get_token

username = "USERNAME"
password = "PASSWORD"
token = get_token(username, password)

sort_by = ["all", "last_login", "week"]
first_semester, second_semester = get_attendance(token, sort_by[0])

"""
get_attendance(token, sort_by) -> list[list[Attendance], list[Attendance]]
Structure of Attendance class:
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

"""

# Printing out the attendance from first semester and their dates
for a in first_semester:
    print()
    print(a.symbol, a.date)
