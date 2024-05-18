Module librus_apix.announcements
================================
This module provides functions for retrieving announcements from the Librus site and parsing them into Announcement objects.

Classes:
    - Announcement: Represents an announcement with attributes for title, author, description, and date.

Functions:
    - get_announcements: Retrieves a list of announcements from the Librus API using a Client object.

Usage:
```python
from librus_apix.client import new_client

# Create a new client instance
client = new_client()
client.get_token(username, password)

# Retrieve announcements
announcements = get_announcements(client)
```

Functions
---------

    
`get_announcements(client: librus_apix.client.Client) ‑> List[librus_apix.announcements.Announcement]`
:   Retrieves a list of announcements from the client.
    
    Args:
        client (Client): The client object used to make the request.
    
    Returns:
        List[Announcement]: A list of Announcement objects representing the retrieved announcements.
    
    Raises:
        ParseError: If there is an error parsing the announcements.

Classes
-------

`Announcement(title: str = '', author: str = '', description: str = '', date: str = '')`
:   Represents an announcement.
    
    Attributes:
        title (str): The title of the announcement.
        author (str): The author of the announcement.
        description (str): The description of the announcement.
        date (str): The date of the announcement.

    ### Class variables

    `author: str`
    :

    `date: str`
    :

    `description: str`
    :

    `title: str`
    :