Module librus_apix.notifications
================================
This module provides functionality to interact with the Librus API and extract notifications from the user's dashboard.

It defines a `Notification` dataclass to encapsulate notification details and includes a function, `get_notifications`,
to fetch and parse notifications from the user's dashboard.

Classes:
    - Notification: Represents a notification with a destination and an amount.

Functions:
    - _extract_name_from_id(id: str) -> str: Extracts a name or identifier from a given ID string.
    - get_notifications(client: Client) -> List[Notification]: Fetches and parses notifications from the user's dashboard on the Librus platform.

Functions
---------

    
`get_notifications(client: librus_apix.client.Client) ‑> List[librus_apix.notifications.Notification]`
:   Fetches and parses notifications from the user's dashboard on the Librus platform.
    
    Args:
        client (Client): An instance of `librus_apix.client.Client` used to make requests to the Librus platform.
    
    Returns:
        List[Notification]: A list of `Notification` objects representing the notifications found on the user's dashboard.

Classes
-------

`Notification(destination: str, amount: int)`
:   Represents a notification with a destination identifier name and an amount.
    
    Attributes:
        destination (str): The identifier extracted from the id like 'ogloszenia', 'wiadomosci'.
        amount (int): The count of notifications for the given destination.

    ### Class variables

    `amount: int`
    :

    `destination: str`
    :