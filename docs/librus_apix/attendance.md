Module librus_apix.attendance
=============================
This module provides functions for retrieving attendance records from the Librus site, parsing them, and calculating attendance frequency.

Classes:
    - Attendance: Represents an attendance record with various attributes such as type, date, teacher, etc.

Functions:
    - get_detail: Retrieves attendance details from a specific URL suffix.
    - get_gateway_attendance: Retrieves attendance data from the Librus gateway API.
    - get_attendance_frequency: Calculates attendance frequency for each semester and overall.
    - get_attendance: Retrieves attendance records from Librus based on specified sorting criteria.

Usage:
```python
from librus_apix.client import new_client

# Create a new client instance
client = new_client()
client.get_token(username, password)

# Retrieve attendance details
detail_url = "example_detail_url"
attendance_details = get_detail(client, detail_url)

# Retrieve attendance data from the gateway API
gateway_attendance = get_gateway_attendance(client)

# Calculate attendance frequency
first_sem_freq, second_sem_freq, overall_freq = get_attendance_frequency(client)

# Retrieve attendance records sorted by a specific criteria
attendance_records = get_attendance(client, sort_by="all")
```

Functions
---------

    
`get_attendance(client: librus_apix.client.Client, sort_by: str = 'all') ‑> List[List[librus_apix.attendance.Attendance]]`
:   Retrieves attendance records from librus.
    
    Args:
        client (Client): The client object used to fetch attendance data.
        sort_by (str, optional): The sorting criteria for attendance records.
            It can be one of the following values:
            - "all": Sort by all attendance records.
            - "week": Sort by attendance records for the current week.
            - "last_login": Sort by attendance records since the last login.
            Defaults to "all".
    
    Returns:
        List[List[Attendance]]: A list containing attendance records grouped by semester.
            Each inner list represents attendance records for a specific semester.
    
    Raises:
        ArgumentError: If an invalid value is provided for the sort_by parameter.
        ParseError: If there is an error parsing the attendance data.

    
`get_attendance_frequency(client: librus_apix.client.Client) ‑> Tuple[float, float, float]`
:   Calculates the attendance frequency for each semester and overall.
    
    Args:
        client (Client): The client object used to retrieve attendance data.
    
    Returns:
        Tuple[float, float, float]: A tuple containing the attendance frequencies for the first semester, second semester, and overall.
            Each frequency is a float value between 0 and 1, representing the ratio of attended lessons to total lessons.
    
    Raises:
        ValueError: If there is an error retrieving attendance data.

    
`get_detail(client: librus_apix.client.Client, detail_url: str) ‑> Dict[str, str]`
:   Retrieves attendance details from the specified detail URL suffix.
    
    Args:
        client (Client): The client object used to make the request.
        detail_url (str): The URL for fetching the attendance details.
    
    Returns:
        Dict[str, str]: A dictionary containing the attendance details.
    
    Raises:
        ParseError: If there is an error parsing the attendance details.

    
`get_gateway_attendance(client: librus_apix.client.Client) ‑> List[Tuple[Tuple[str, str], str, str]]`
:   Retrieves attendance data from the gateway API.
    
    The gateway API data is typically updated every 3 hours.
    Accessing api.librus.pl requires a private key.
    
    Requires:
        oauth token to be refreshed with client.refresh_oauth()
    
    Args:
        client (Client): The client object used to make the request.
    
    Returns:
        List[Tuple[Tuple[str, str], str, str]]: A list of tuples containing attendance data.
            Each tuple contains three elements:
            1. Tuple containing type abbreviation and type name.
            2. Lesson number.
            3. Semester.
    
    Raises:
        ValueError: If the OAuth token is missing.
        AuthorizationError: If there is an authorization error while accessing the API.

Classes
-------

`Attendance(symbol: str, href: str, semester: int, date: str, type: str, teacher: str, period: int, excursion: bool, topic: str, subject: str)`
:   Represents an attendance record.
    
    Attributes:
        symbol (str): The symbol representing the attendance record.
        href (str): The URL associated with the attendance record.
        semester (int): The semester number to which the attendance record belongs.
        date (str): The date of the attendance record.
        type (str): The type of attendance (e.g., absence, presence).
        teacher (str): The name of the teacher associated with the attendance record.
        period (int): The period or hour of the attendance record.
        excursion (bool): Indicates if the attendance record is related to an excursion.
        topic (str): The topic or subject of the attendance record.
        subject (str): The school subject associated with the attendance record.

    ### Class variables

    `date: str`
    :

    `excursion: bool`
    :

    `href: str`
    :

    `period: int`
    :

    `semester: int`
    :

    `subject: str`
    :

    `symbol: str`
    :

    `teacher: str`
    :

    `topic: str`
    :

    `type: str`
    :