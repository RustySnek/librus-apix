Module librus_apix.completed_lessons
====================================
This module provides functions for managing completed lessons from the Librus site, including retrieval, parsing, and pagination.

Classes:
    - Lesson: Represents a completed lesson with attributes such as subject, teacher, topic, etc.

Functions:
    - get_max_page_number: Retrieves the maximum page number for completed lessons within a specified date range.
    - get_completed: Retrieves completed lessons within a specified date range and page number.

Usage:
```python
from librus_apix.client import new_client

# Create a new client instance
client = new_client()
client.get_token(username, password)

# Retrieve the maximum page number for completed lessons within a date range
date_from = "YYYY-MM-DD"
date_to = "YYYY-MM-DD"
max_page_number = get_max_page_number(client, date_from, date_to)

# Retrieve completed lessons within a specified date range and page number
page_number = 0  # Specify the page number
completed_lessons = get_completed(client, date_from, date_to, page=page_number)
```

Functions
---------

    
`get_completed(client: librus_apix.client.Client, date_from: str, date_to: str, page: int = 0) ‑> List[librus_apix.completed_lessons.Lesson]`
:   Retrieves completed lessons within a specified date range and page number.
    
    Args:
        client (Client): The client object used to fetch completed lesson data.
        date_from (str): The start date of the date range (in format "YYYY-MM-DD").
        date_to (str): The end date of the date range (in format "YYYY-MM-DD").
        page (int, optional): The page number of the completed lessons to retrieve.
            Defaults to 0.
    
    Returns:
        List[Lesson]: A list of Lesson objects representing the completed lessons.
    
    Notes:
        - The date_from and date_to parameters do not have a limit on how far apart they can be.
        - If date_from or date_to is empty, it returns completed lessons from the past week.
        - Each page contains 15 lessons. The maximum number of pages can be retrieved using the get_max_page_number() function.
        - If the specified page number exceeds the maximum, it defaults to the maximum available page.

    
`get_max_page_number(client: librus_apix.client.Client, date_from: str, date_to: str) ‑> int`
:   Retrieves the maximum page number for completed lessons within a specified date range.
    
    Args:
        client (Client): The client object used to fetch completed lesson data.
        date_from (str): The start date of the date range (in format "YYYY-MM-DD").
        date_to (str): The end date of the date range (in format "YYYY-MM-DD").
    
    Returns:
        int: The maximum page number for the completed lessons within the specified date range.
    
    Raises:
        ParseError: If there is an error while trying to retrieve the maximum page number.

Classes
-------

`Lesson(subject: str, teacher: str, topic: str, z_value: str, attendance_symbol: str, attendance_href: str, lesson_number: int, weekday: str, date: str)`
:   Represents a lesson.
    
    Attributes:
        subject (str): The subject of the lesson.
        teacher (str): The teacher teaching the lesson.
        topic (str): The topic or content of the lesson.
        z_value (str): The z in librus. No clue what it stands for.
        attendance_symbol (str): The symbol representing attendance for the lesson.
        attendance_href (str): The URL associated with the attendance record for the lesson.
        lesson_number (int): The number of the lesson.
        weekday (str): The weekday on which the lesson occurs.
        date (str): The date of the lesson.

    ### Class variables

    `attendance_href: str`
    :

    `attendance_symbol: str`
    :

    `date: str`
    :

    `lesson_number: int`
    :

    `subject: str`
    :

    `teacher: str`
    :

    `topic: str`
    :

    `weekday: str`
    :

    `z_value: str`
    :