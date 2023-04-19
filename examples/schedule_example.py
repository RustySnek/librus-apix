from librus_apix.schedule import get_schedule, schedule_detail
from librus_apix.get_token import get_token

username = "USERNAME"
password = "PASSWORD"
token = get_token(username, password)

"""
get_schedule returns all days and their events from the month and year provided.
get_schedule(token, month, year) -> dict[str, list[Event]]

Structure of Event class:
    class Event:
        title: str
        subject: str
        data: list[str] | contains a list of attributes ex. ['lesson number: 5', 'English Exam']
        day: str
        number: Union[int, str]
        hour: str
        href: str
"""

month = '2'
year = '2023'
schedule = get_schedule(token, month, year)

# Printing out all events in the month
for day in schedule:
    for event in schedule[day]:
        print()
        print(event.title)
        # Check if Event has an href before accessing it
        if event.href == "":
            continue
        prefix, href = event.href.split('/')
        details = schedule_detail(token, prefix, href)
        print('\n'.join([f'{key}: {value}' for key,value in details.items()]))
