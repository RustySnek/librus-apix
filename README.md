<p align="center">
  <img src="https://github.com/RustySnek/librus-apix/blob/main/logo.png" alt="librus-apix logo"/>
</p>

# Librus Synergia web scraper.
### Be sure to visit the [documentation](https://rustysnek.github.io/librus-apix/).


## Installation

```sh
pip install librus-apix
```

> [!IMPORTANT]  
> It's advised to [run all tests](#running-tests) before trying everything out.  Some schools have different librus setups which may cause errors/warnings  If you find any open an issue or contribute with a PR


## Running tests
### First, follow the [steps to clone the repo and install librus-apix locally](#working-on-the-project), then install pytest.
```bash
pip install pytest
```
### Run the tests
  #### [Retrieve your token key](#save-and-load-token) and test on actual data  
  
  ```bash
  pytest --token {output of token.API_Key}
  ```
  
  #### [Dev] Test using a mock server
  - For developing purposes I've created a [simple mock html server](https://github.com/RustySnek/librus-apix-mock)

    ```bash
    # generate all html pages and run server
    python scripts/generate_all.py
    python server.py
    # now unless you've changed the server.py default port you should be good to go and run
    pytest
    # if you did change the port, you have to edit the tests/conftest.py file accordingly
    ```

# Quick Start

## Setting up client
```py
from librus_apix.client import Client, Token, new_client

# create a new client with empty Token()
client: Client = new_client()
# update the token
_token: Token = client.get_token("username", "password")
# now you can pass your client to librus-apix functions
```
### Save and Load token
```py
from librus_apix.client import Token, Client, new_client

key = client.token.API_Key

# you can store this key and later load it in ways like this:
## Load directly into token object
token = Token(API_Key=token_key)
client: Client = new_client(token=token)
## or put it into existing client
client.token = token
## or into empty token
client.token.API_Key = key

```
### Getting the Math grades

```py
from librus_apix.grades import get_grades

grades, average_grades, descriptive_grades = get_grades(client)

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

announcements = get_announcements(client)

for a in announcements:
  print(a.description)

```

### Getting the attendance
```py
from librus_apix.attendance import get_attendance

first_semester, second_semester = get_attendance(client)

for attendance in first_semester:
  print(attendance.symbol, attendance.date)

```

### Getting the attendance frequency
```py
from librus_apix.attendance import get_attendance_frequency

first, second, overall = get_attendance_frequency(client)
print(f"{first*100}%")

```

### Getting the Homework
```py
from librus_apix.homework import get_homework, homework_detail

# date from-to up to 1 month 
date_from = '2023-03-02'
date_to = '2023-03-30'

homework = get_homework(client, date_from, date_to)

for h in homework:
  print(h.lesson, h.completion_date)
  href = h.href
  details = homework_detail(client, href)
  print(details)

```

### Sending Messages
```py
from librus_apix.messages import recipient_groups, get_recipients, send_message

groups = recipient_groups(client)
recipients = get_recipients(client, groups[0])
my_recipient = recipients["John Brown"]
my_second_recipient = recipients["Barbara Brown"]

sent = send_message(client,
                   "Message Title",
                   "Message\n content",
                   [my_recipient, my_second_recipient]
)
if sent == True:
  print("Sent!")
else:
  print("Error sending a message!")
```

### Getting the Messages
```py
from librus_apix.messages import get_received, message_content

messages = get_received(client, page=1)
for message in messages:
  print(message.title)
  href = message.href
  print(message_content(client, href))

```

### Getting the Schedule

```py
from librus_apix.schedule import get_schedule, schedule_detail
month = '2'
year = '2023'
schedule = get_schedule(client, month, year)
for day in schedule:
  for event in schedule[day]:
    print(event.title)
    prefix, href = event.href.split('/')
    details = schedule_detail(client, prefix, href)
    print(details)

```

### Getting the Timetable

```py
from datetime import datetime
from librus_apix.timetable import get_timetable

monday_date = '2023-04-3'
monday_datetime = datetime.strptime(monday_date, '%Y-%m-%d')
timetable = get_timetable(client, monday_datetime)
for weekday in timetable:
  for period in timetable[weekday]:
    print(period.subject, period.teacher_and_classroom)

```

### Notifications (a.k.a. spamming endpoints)
```
# initial should be always called with a new token
initial_notifications, new_ids = get_initial_notification_data(client)
sleep(150)
# after that you retrieve the new Notifications with new_ids filtered out 
new_notifications, new_ids = get_new_notification_data(client, new_ids)
# see more in docs
```

### Getting the lucky number
```py
from librus_apix.student_information import student_information

info = student_information(client)
print(info.lucky_number)
```

### Adding a proxy
```py
# Proxy can be added with
client = new_client(proxy={"https": "http://my-proxy.xyz"})
# or
client.proxy = {"https": "http://my-proxy.xyz"}
```

## Working On The Project

```sh
git clone https://github.com/RustySnek/librus-apix
cd librus-apix
python -m venv venv
source ./venv/bin/activate
pip install requirements.txt
# Installing library with editable flag
pip install -e .
```
