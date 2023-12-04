# Librus Synergia web scraper.

## Installation

```sh
pip install librus-apix
```

## Quick Start

## Getting the Token
```py
from librus_apix.get_token import get_token

token = get_token("Username", "Password")
```
### Getting the Math grades

```py
from librus_apix.grades import get_grades

grades, average_grades, descriptive_grades = get_grades(token)

for semester in grades:
  for mark in semester["Mathematics"]:
      print(mark.grade)
for semester in descriptive_grades:
  for mark in semester["Emotional development"]:
      print(mark.grade)
```

### Getting the Announcements
```py
from librus_apix.announcements import get_announcements

announcements = get_announcements(token)

for a in announcements:
  print(a.description)

```

### Getting the attendance
```py
from librus_apix.attendance import get_attendance

first_semester, second_semester = get_attendance(token)

for attendance in first_semester:
  print(attendance.symbol, attendance.date)

```

### Getting the Homework
```py
from librus_apix.homework import get_homework, homework_detail

# date from-to up to 1 month 
date_from = '2023-03-02'
date_to = '2023-03-30'

homework = get_homework(token, date_from, date_to)

for h in homework:
  print(h.lesson, h.completion_date)
  href = h.href
  details = homework_detail(token, href)
  print(details)

```

### Getting the Messages
```py
from librus_apix.messages import get_recieved, message_content

messages = get_recieved(token, page=1)
for message in messages:
  print(message.title)
  href = message.href
  print(message_content(token, href))

```

### Getting the Schedule

```py
from librus_apix.schedule import get_schedule, schedule_detail
month = '2'
year = '2023'
schedule = get_schedule(token, month, year)
for day in schedule:
  for event in schedule[day]:
    print(event.title)
    prefix, href = event.href.split('/')
    details = schedule_detail(token, prefix, href)
    print(details)

```

### Getting the Timetable

```py
from datetime import datetime
from librus_apix.timetable import get_timetable

monday_date = '2023-04-3'
monday_datetime = datetime.strptime(monday_date, '%Y-%m-%d')
timetable = get_timetable(token, monday_datetime)
for weekday in timetable:
  for period in timetable[weekday]:
    print(period.subject, period.teacher_and_classroom)

```


### Getting the lucky number
```py
from librus_apix.student_information import student_information

info = student_information(token)
print(info.lucky_number)
```

## Working on the Project

```sh
git clone https://github.com/RustySnek/librus-apix
cd librus-apix
python -m venv venv
source ./venv/bin/activate
pip install requirements.txt
# Installing library with editable flag
pip install -e .
```
