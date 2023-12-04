from librus_apix.completed_lessons import get_completed, get_max_page_number
from librus_apix.get_token import get_token

username = "USERNAME"
password = "PASSWORD"

token = get_token(username, password)

"""
date_from and date_to are date strings with format: '%Y-%m-%d'
They can be left as empty strings which should return the past week (not exactly sure if it's the whole week atm.)

Each page of completed_lessons contains up to 15 lessons

Structure of Lesson class:
    class Lesson:
        subject: str
        teacher: str
        topic: str
        z_value: str | Currently unknown since this table is empty for me. Lmk if it returns anything to you.
        attendance_symbol: str
        attendance_href: str | Can be used with the get_detail() fuunction from librus_apix.attendance module.
        lesson_number: int
        weekday: str
        date: str
"""

# Printing out the first 15 lessons from the past week
date_from = ""
date_to = ""

page = get_max_page_number(token, date_from, date_to)
completed_lessons = get_completed(token, date_from, date_to, page - 1)
for lesson in completed_lessons:
    print(lesson.lesson_number, lesson.subject)
