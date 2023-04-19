from librus_apix.attendance import get_attendance
from librus_apix.get_token import get_token

username = "USERNAME"
password = "PASSWORD"
token = get_token(username, password)

first_semester, second_semester = get_attendance(token)

"""
get_attendance(token) -> list[list[Attendance], list[Attendance]]
Structure of Attendance class:
    class Attendance:
        symbol: str
        href: str
        semester: int
        attributes: dict | Contains all of the attributes ex. {'Date': '2023-02-08'}
"""

# Printing out the attendance from first semester and it's attributes
for a in first_semester:
    print()
    print(a.symbol)
    print("\n".join([f"{key}: {value}" for key, value in a.attributes.items()]))
