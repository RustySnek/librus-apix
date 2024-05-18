Module librus_apix.homework
===========================
This module provides functions for retrieving homework assignments from the Librus site, parsing them, and fetching detailed information about specific assignments.

Classes:
    - Homework: Represents a homework assignment with detailed information such as lesson, teacher, subject, etc.

Functions:
    - homework_detail: Retrieves detailed information about a specific homework assignment.
    - get_homework: Retrieves homework assignments within a specified date range.

Usage:
```python
from librus_apix.client import new_client

# Create a new client instance
client = new_client()
client.get_token(username, password)

# Retrieve homework assignments within a specified date range
date_from = "YYYY-MM-DD"
date_to = "YYYY-MM-DD"
homework_assignments = get_homework(client, date_from, date_to)

# Retrieve detailed information about a specific homework assignment
for homework in homework_assignments:
    homework_details = homework_detail(client, homework.href)
```

Functions
---------

    
`get_homework(client: librus_apix.client.Client, date_from: str, date_to: str) ‑> List[librus_apix.homework.Homework]`
:   Fetches and parses the list of homework assignments within a specified date range.
    
    Args:
        client (Client): The client object used to interact with the server.
        date_from (str): The start date for fetching homework assignments (format: 'YYYY-MM-DD').
        date_to (str): The end date for fetching homework assignments (format: 'YYYY-MM-DD').
    
    Returns:
        List[Homework]: A list of Homework objects representing the homework assignments within the specified date range.
    
    Raises:
        ParseError: If there is an error in parsing the homework assignments.

    
`homework_detail(client: librus_apix.client.Client, detail_url: str) ‑> Dict[str, str]`
:   Fetches and parses detailed information about a specific homework assignment.
    
    Args:
        client (Client): The client object used to interact with the server.
        detail_url (str): The URL suffix to fetch the detailed homework information.
    
    Returns:
        Dict[str, str]: A dictionary containing detailed homework information where the keys are detail labels
                        and the values are the corresponding detail values.
    
    Raises:
        ParseError: If there is an error in parsing the homework details.

Classes
-------

`Homework(lesson: str, teacher: str, subject: str, category: str, task_date: str, completion_date: str, href: str)`
:   Represents a homework assignment with detailed information.
    
    Attributes:
        lesson (str): The lesson or topic associated with the homework.
        teacher (str): The name of the teacher who assigned the homework.
        subject (str): The subject for which the homework is assigned.
        category (str): The category or type of homework (e.g., assignment, project).
        task_date (str): The date when the homework was assigned.
        completion_date (str): The date by which the homework needs to be completed.
        href (str): A URL suffix or link associated with the homework for more details.

    ### Class variables

    `category: str`
    :

    `completion_date: str`
    :

    `href: str`
    :

    `lesson: str`
    :

    `subject: str`
    :

    `task_date: str`
    :

    `teacher: str`
    :