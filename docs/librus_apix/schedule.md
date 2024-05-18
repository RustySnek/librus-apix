Module librus_apix.schedule
===========================
This module provides functions for retrieving schedule information from the Librus site, parsing it, and formatting it into a structured representation.

Classes:
    - Event: Represents an event in the schedule with various attributes like title, subject, day, etc.

Functions:
    - schedule_detail: Fetches detailed schedule information for a specific prefix and detail URL suffix.
    - get_schedule: Fetches the schedule for a specific month and year.

Usage:
    ```python
    from librus_apix.client import new_client

    # Create a new client instance
    client = new_client()
    client.get_token(username, password)

    # Fetch the schedule for a specific month and year
    month = "01"
    year = "2024"
    include_empty = True
    monthly_schedule = get_schedule(client, month, year, include_empty)

    # Fetch detailed schedule information
    day_one = monthly_schedule[1].href
    prefix, suffix = day_one.split("/")
    detailed_schedule = schedule_detail(client, prefix, detail_url)
    ```

Functions
---------

    
`get_schedule(client: librus_apix.client.Client, month: str, year: str, include_empty: bool = False) ‑> DefaultDict[int, List[librus_apix.schedule.Event]]`
:   Fetches the schedule for a specific month and year.
    
    Args:
        client (Client): The client object for making HTTP requests.
        month (str): The month for which the schedule is requested.
        year (str): The year for which the schedule is requested.
        include_empty (bool, optional): Flag to include empty schedules. Defaults to False.
    
    Returns:
        DefaultDict[int, List[Event]]: A dictionary containing the schedule for each day of the month.

    
`schedule_detail(client: librus_apix.client.Client, prefix: str, detail_url: str) ‑> Dict[str, str]`
:   Fetches the detailed schedule information for a specific prefix and detail URL suffix.
    
    Args:
        client (Client): The client object for making HTTP requests.
        prefix (str): The prefix of the schedule URL.
        detail_url (str): The detail URL of the schedule.
    
    Returns:
        Dict[str, str]: A dictionary containing schedule details.

Classes
-------

`Event(title: str, subject: str, data: dict, day: str, number: Union[int, str], hour: str, href: str)`
:   Represents an event in the schedule.
    
    Attributes:
        title (str): The title of the event.
        subject (str): The subject of the event.
        data (dict): Additional data associated with the event.
        day (str): The day on which the event occurs.
        number (Union[int, str]): The number associated with the event.
        hour (str): The hour at which the event occurs.
        href (str): 'prefix'/'suffix' joined with a slash (this should be reworked...).

    ### Class variables

    `data: dict`
    :

    `day: str`
    :

    `hour: str`
    :

    `href: str`
    :

    `number: Union[int, str]`
    :

    `subject: str`
    :

    `title: str`
    :