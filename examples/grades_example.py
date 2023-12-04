from librus_apix.get_token import get_token
from librus_apix.grades import get_grades

username = "USERNAME"
password = "PASSWORD"
token = get_token(username, password)

"""
The second argument "sort_by" of get_grades() function is used to retrieve the grades from the last login or the past week.
"""
sort_by = ["all", "week", "last_login"]  # All of the options for sort_by argument
grades, semester_grades, descriptive_grades = get_grades(token, sort_by[0])

"""
The grades structure looks as follows:
    grades = [
        {
            "History": list[Grade],
            "Mathematics": list[Grade],
            ...
        },
        {
            "History": list[Grade],
            "Mathematics": list[Grade],
            ...
        }
    ]

The Grade class contains the following variables:
    class Grade:
        title: str
        grade: str | A string representation of the grade ex. '4+'
        counts: bool | If grade counts to semester average it is True else it's False
        date: str
        href: str
        desc: str | Description of the mark
        semester: int
        category: str | Category of the mark ex. 'Semester Exam'
        teacher: str
        weight: int
        value: [float, str] | Property function that returns a real value of the mark ex. '4+' is 4.75.
                            | If the mark is '-' or '+' it returns 'Does not count'.

The descriptive grades structure looks as follows:
    grades = [
        {
            "History": list[GradeDescriptive],
            "Mathematics": list[GradeDescriptive],
            ...
        },
        {
            "History": list[GradeDescriptive],
            "Mathematics": list[GradeDescriptive],
            ...
        }
    ]

The GradeDescriptive class contains the following variables:
    class GradeDescriptive:
        title: str
        grade: str | A string representation of the grade ex. '4+'
        date: str
        href: str
        desc: str | Description of the mark
        semester: int
        teacher: str
"""
# Printing out the first three marks of all subjects in the first semester.

first_semester, second_semester = grades
for subject in first_semester:
    initial_three_grades = first_semester[subject][:3]
    print(f"Subject: {subject}")
    for mark in initial_three_grades:
        print(f"\t|{mark.grade}| - {mark.date}")

first_semester, second_semester = descriptive_grades
for subject in first_semester:
    initial_three_grades = first_semester[subject][:3]
    print(f"Subject: {subject}")
    for mark in initial_three_grades:
        print(f"\t|{mark.grade}| - {mark.date}")
