from librus_apix.homework import get_homework, homework_detail
from librus_apix.get_token import get_token

username = "USERNAME"
password = "PASSWORD"
token = get_token(username, password)
"""
Homework takes date_from and date_to as arguments.
The dates shouldn't be more than a month apart.
Format '%Y-%m-%d'
"""
date_from = "2023-03-02"
date_to = "2023-03-30"
homework = get_homework(token, date_from, date_to)

"""
homework(token, date_from, date_to) -> list[Homework]

Structure of Homework class:
    class Homework:
        lesson: str
        teacher: str
        subject: str
        category: str
        task_date: str
        completion_date: str
        href: str
"""

# Printing out homework and its details from between the dates.
for h in homework:
    print()
    print(h.lesson, h.completion_date)
    details = homework_detail(token, h.href)
    print("\n".join([f"{key}: {value}" for key, value in details.items()]))
