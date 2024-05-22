Module librus_apix.messages
===========================
This module provides functions for interacting with messages in the Librus messaging system, including sending, retrieving, and parsing messages.

Classes:
    - Message: Represents a message with details like author, title, date, etc.
    - MessageData: Represents the data of a message content.

Functions:
    - recipient_groups: Retrieves the list of recipient groups available for sending messages.
    - get_recipients: Retrieves the recipients belonging to a specific group.
    - send_message: Sends a message to selected recipients.
    - message_content: Retrieves the content of a message.
    - get_max_page_number: Retrieves the maximum page number of messages.
    - get_received: Retrieves received messages from a specific page.
    - get_sent: Retrieves sent messages from a specific page.

Usage:
    ```py

        from librus_apix.client import new_client

        # Create a new client instance
        client = new_client()
        client.get_token(username, password)

        # Retrieve recipient groups and recipients
        groups = recipient_groups(client)
        recipients = get_recipients(client, groups[0])

        # Send a message
        title = "Test Message"
        content = "This is a test message."
        recipient_ids = list(recipients.values())
        success, result_message = send_message(client, title, content, recipient_ids)

        # Get received/sent messages
        messages = get_sent(client, page=1)
        messages = get_received(client, page=1)
        ...
        # Retrieve content of a message
        for message in messages:
            content = message_content(client, message.href)
            ...
    ```

Functions
---------

    
`get_max_page_number(client: librus_apix.client.Client) ‑> int`
:   Retrieves the maximum page number of messages.
    
    Args:
        client (Client): The client object for making HTTP requests.
    
    Returns:
        int: The maximum page number.

    
`get_received(client: librus_apix.client.Client, page: int) ‑> List[librus_apix.messages.Message]`
:   Retrieves received messages from a specific page.
    
    Args:
        client (Client): The client object for making HTTP requests.
        page (int): The page number of messages to retrieve.
    
    Returns:
        List[Message]: A list of received Message objects.

    
`get_recipients(client: librus_apix.client.Client, group: str)`
:   Retrieves the recipients belonging to a specific group.
    
    Args:
        client (Client): The client object for making HTTP requests.
        group (str): The identifier of the recipient group.
    
    Returns:
        dict: A dictionary mapping teacher names to their IDs.

    
`get_sent(client: librus_apix.client.Client, page: int) ‑> List[librus_apix.messages.Message]`
:   Retrieves sent messages from a specific page.
    
    Args:
        client (Client): The client object for making HTTP requests.
        page (int): The page number of messages to retrieve.
    
    Returns:
        List[Message]: A list of sent Message objects.

    
`message_content(client: librus_apix.client.Client, content_url: str) ‑> librus_apix.messages.MessageData`
:   Retrieves the content of a message.
    
    Args:
        client (Client): The client object for making HTTP requests.
        content_url (str): The URL of the message content.
    
    Returns:
        MessageData: An object containing the message details.

    
`parse(message_soup: bs4.BeautifulSoup) ‑> List[librus_apix.messages.Message]`
:   Parses received messages from the message soup.
    
    Args:
        message_soup (BeautifulSoup): The BeautifulSoup object containing message data.
    
    Returns:
        List[Message]: A list of Message objects representing received messages.

    
`parse_sent(message_soup: bs4.BeautifulSoup) ‑> List[librus_apix.messages.Message]`
:   Parses sent messages from the message soup.
    
    Args:
        message_soup (BeautifulSoup): The BeautifulSoup object containing message data.
    
    Returns:
        List[Message]: A list of Message objects representing sent messages.

    
`recipient_groups(client: librus_apix.client.Client) ‑> List[str]`
:   Retrieves the list of recipient groups available for sending messages.
    
    Args:
        client (Client): The client object for making HTTP requests.
    
    Returns:
        List[str]: A list of recipient group identifiers.

    
`send_message(client: librus_apix.client.Client, title: str, content: str, recipient_ids: list[str]) ‑> Tuple[bool, str]`
:   Sends a message to selected recipients.
    
    Args:
        client (Client): The client object for making HTTP requests.
        title (str): The title of the message.
        content (str): The content of the message.
        recipient_ids (list[str]): The list of recipient IDs.
    
    Returns:
        Tuple[bool, str]: A tuple indicating whether the message was sent successfully
        and the result message.

    
`unwrap_message_data(tr: bs4.element.Tag) ‑> str`
:   

Classes
-------

`Message(author: str, title: str, date: str, href: str, unread: bool, has_attachment: bool)`
:   Represents a message.
    
    Attributes:
        author (str): The author of the message.
        title (str): The title of the message.
        date (str): The date when the message was sent.
        href (str): The URL reference to the message.
        unread (bool): Indicates if the message is unread.
        has_attachment (bool): Indicates if the message has attachments.

    ### Class variables

    `author: str`
    :

    `date: str`
    :

    `has_attachment: bool`
    :

    `href: str`
    :

    `title: str`
    :

    `unread: bool`
    :

`MessageData(author: str, title: str, content: str, date: str)`
:   Represents the data of a message content.
    
    Attributes:
        author (str): The author of the message.
        title (str): The title of the message.
        content (str): The content of the message.
        date (str): The date when the message was sent.

    ### Class variables

    `author: str`
    :

    `content: str`
    :

    `date: str`
    :

    `title: str`
    :