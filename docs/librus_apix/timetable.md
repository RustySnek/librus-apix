Module librus_apix.timetable
============================
Module: timetable_parser

Description:
This module provides functions for parsing and retrieving timetable data from an educational institution's website.

Classes:
    - Period: Represents a period of a class with relevant information.

Functions:
    - get_timetable: Retrieves the timetable for a given week starting from a Monday date.

Exceptions:
    - DateError: Raised when the provided date is not a Monday.
    - ParseError: Raised when there's an error while parsing the timetable.

Usage:
```python
from your_client_module import Client  # import your client module here

# Example usage:
client = Client()  # initialize your client
monday_date = datetime(2024, 5, 13)  # example Monday date
try:
    timetable = get_timetable(client, monday_date)
    for day in timetable:
        for period in day:
            print(period.subject, period.date, period.date_from, period.date_to)
except DateError as e:
    print(e)
except ParseError as e:
    print(e)
```

Functions
---------

    
`get_timetable(client: librus_apix.client.Client, monday_date: datetime.datetime) ‑> List[List[librus_apix.timetable.Period]]`
:   Retrieves the timetable for a given week starting from a Monday date.
    
    Args:
        client (Client): An instance of the client class for fetching data.
        monday_date (datetime): The Monday date for the week's timetable.
    
    Returns:
        List[List[Period]]: A nested list containing periods for each day of the week.
    
    Raises:
        DateError: If the provided date is not a Monday.
        ParseError: If there's an error while parsing the timetable.

Classes
-------

`Period(subject: str, teacher_and_classroom: str, date: str, date_from: str, date_to: str, weekday: str, info: Dict[str, str], number: int, next_recess_from: Optional[str], next_recess_to: Optional[str])`
:   Represents a period of a class with relevant information.
    
    Attributes:
        subject (str): The subject of the class.
        teacher_and_classroom (str): Combined information of teacher and classroom.
        date (str): The date of the period.
        date_from (str): Starting time of the period.
        date_to (str): Ending time of the period.
        weekday (str): The day of the week of the period.
        info (Dict[str, str]): Additional information about the period.
        number (int): The number of the period within a day.
        next_recess_from (str | None): Starting time of the next recess, if any.
        next_recess_to (str | None): Ending time of the next recess, if any.

    ### Class variables

    `date: str`
    :

    `date_from: str`
    :

    `date_to: str`
    :

    `info: Dict[str, str]`
    :

    `next_recess_from: Optional[str]`
    :

    `next_recess_to: Optional[str]`
    :

    `number: int`
    :

    `subject: str`
    :

    `teacher_and_classroom: str`
    :

    `weekday: str`
    :