"""
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
"""

from typing import List, Tuple
from bs4 import BeautifulSoup, Tag
from librus_apix.client import Client
from librus_apix.exceptions import ParseError
from librus_apix.helpers import no_access_check
from dataclasses import dataclass
import re


@dataclass
class MessageData:
    """
    Represents the data of a message content.

    Attributes:
        author (str): The author of the message.
        title (str): The title of the message.
        content (str): The content of the message.
        date (str): The date when the message was sent.
    """

    author: str
    title: str
    content: str
    date: str


@dataclass
class Message:
    """
    Represents a message.

    Attributes:
        author (str): The author of the message.
        title (str): The title of the message.
        date (str): The date when the message was sent.
        href (str): The URL reference to the message.
        unread (bool): Indicates if the message is unread.
        has_attachment (bool): Indicates if the message has attachments.
    """

    author: str
    title: str
    date: str
    href: str
    unread: bool
    has_attachment: bool


def recipient_groups(client: Client) -> List[str]:
    """
    Retrieves the list of recipient groups available for sending messages.

    Args:
        client (Client): The client object for making HTTP requests.

    Returns:
        List[str]: A list of recipient group identifiers.
    """
    soup = no_access_check(
        BeautifulSoup(client.get(client.RECIPIENT_GROUPS_URL).text, "lxml")
    )
    groups = []
    trs = soup.select("table.message-recipients > tbody > tr")
    for tr in trs:
        radio = tr.select_one("input.recipiantTypeRadio")
        if radio is None:
            raise ParseError("Error getting groups (radio)")
        groups.append(radio.attrs.get("value", ""))
    return groups


def get_recipients(client: Client, group: str):
    """
    Retrieves the recipients belonging to a specific group.

    Args:
        client (Client): The client object for making HTTP requests.
        group (str): The identifier of the recipient group.

    Returns:
        dict: A dictionary mapping teacher names to their IDs.
    """
    payload = {
        "typAdresata": group,
        "poprzednia": "5",
        "tabZaznaczonych": "",
        "czyWirtualneKlasy": False,
        "idGrupy": "0",
    }
    soup = no_access_check(
        BeautifulSoup(client.post(client.RECIPIENTS_URL, data=payload).text, "lxml")
    )
    labels = soup.select("label")
    teachers = {}
    for label in labels:
        teachers[label.text.replace("\xa0", "")] = label.attrs.get("for", "_").split(
            "_"
        )[-1]
    return teachers


def send_message(
    client: Client,
    title: str,
    content: str,
    recipient_ids: list[str],
) -> Tuple[bool, str]:
    """
    Sends a message to selected recipients.

    Args:
        client (Client): The client object for making HTTP requests.
        title (str): The title of the message.
        content (str): The content of the message.
        recipient_ids (list[str]): The list of recipient IDs.

    Returns:
        Tuple[bool, str]: A tuple indicating whether the message was sent successfully
        and the result message.
    """
    payload = {
        "filtrUzytkownikow": "0",
        "idPojemnika": "",
        "DoKogo": recipient_ids,
        "Rodzaj": "0",
        "temat": title,
        "tresc": content,
        "poprzednia": "5",
        "fileStorageIdentifier": "",
        "wyslij": "Wyślij",
    }
    sent_message = no_access_check(
        BeautifulSoup(client.post(client.SEND_MESSAGE_URL, data=payload).text, "lxml")
    )
    result = sent_message.select_one("div.container-background > p")
    if result is None:
        raise ParseError("Error getting the result of the message!")
    result = result.text
    if "nie zostala" in result:
        return False, result
    if sent_message.status_code == 200:
        return True, result
    return False, result


def unwrap_message_data(tr: Tag) -> str:
    value = tr.select_one("td[class='left']")
    return value.text if value is not None else ""


def message_content(client: Client, content_url: str) -> MessageData:
    """
    Retrieves the content of a message.

    Args:
        client (Client): The client object for making HTTP requests.
        content_url (str): The URL of the message content.

    Returns:
        MessageData: An object containing the message details.
    """
    soup = no_access_check(
        BeautifulSoup(client.get(client.MESSAGE_URL + "/" + content_url).text, "lxml")
    )
    message_data = soup.select_one("table[class='stretch']")
    if message_data is None:
        raise ParseError("Error in parsing message data.")
    trs = message_data.select("tr")
    if len(trs) < 3:
        raise ParseError("Not enough values to unpack from message_data")
    author, title, date = trs[:3]
    content = soup.find("div", attrs={"class": "container-message-content"})
    if content is None:
        raise ParseError("Error in parsing message content.")
    return MessageData(
        unwrap_message_data(author),
        unwrap_message_data(title),
        content.text,
        unwrap_message_data(date),
    )


def _sanitize_href(href: str) -> str:
    if len(href) > 4:
        return href.split("/")[4]
    return ""


def parse_sent(message_soup: BeautifulSoup) -> List[Message]:
    """
    Parses sent messages from the message soup.

    Args:
        message_soup (BeautifulSoup): The BeautifulSoup object containing message data.

    Returns:
        List[Message]: A list of Message objects representing sent messages.
    """
    msgs: List[Message] = []
    hasAttachment = False
    soup = message_soup.find("table", attrs={"class": "decorated stretch"})
    if soup is None:
        raise ParseError("Error in parsing messages.")
    tbody = soup.find("tbody")
    if not isinstance(tbody, Tag):
        raise ParseError("Error in parsing messages (tbody).")
    tds = tbody.find_all("tr", attrs={"class": ["line0", "line1"]})
    if tds[0].text.strip() == "Brak wiadomości":
        return []
    for td in tds:
        hasAttachment = False
        message_data: List[Tag] = td.find_all("td")
        if len(message_data) < 7:
            raise ParseError("Message data has less than 7 elements")
        _tick, attachment, author, title, date, unread, _trash = message_data[:7]
        if attachment.find("img"):
            hasAttachment = True
        unread = True if unread == "NIE" else False
        author_a = author.find("a")
        href = ""
        if isinstance(author_a, Tag):
            href = author_a.attrs.get("href", "")
            href = _sanitize_href(href)
        author = author.text
        title = title.text
        date = date.text
        m = Message(author, title, date, href, unread, hasAttachment)
        msgs.append(m)
    return msgs


def parse(message_soup: BeautifulSoup) -> List[Message]:
    """
    Parses received messages from the message soup.

    Args:
        message_soup (BeautifulSoup): The BeautifulSoup object containing message data.

    Returns:
        List[Message]: A list of Message objects representing received messages.
    """
    msgs: List[Message] = []
    hasAttachment = False
    soup = message_soup.find("table", attrs={"class": "decorated stretch"})
    if soup is None:
        raise ParseError("Error in parsing messages.")
    tbody = soup.find("tbody")
    if not isinstance(tbody, Tag):
        raise ParseError("Error in parsing messages (tbody).")
    tds = tbody.find_all("tr", attrs={"class": ["line0", "line1"]})
    if tds[0].text.strip() == "Brak wiadomości":
        return []
    for td in tds:
        unread = False
        hasAttachment = False
        message_data: List[Tag] = td.find_all("td")
        if len(message_data) < 6:
            raise ParseError("Message data has less than 6 elements")
        _tick, attachment, author, title, date, _trash = message_data[:6]
        if attachment.find("img"):
            hasAttachment = True
        style = title.get("style")
        if not isinstance(style, List) and not isinstance(style, str):
            style = []
        if "font-weight: bold" in style:
            unread = True

        author_a = author.find("a")
        href = ""
        if isinstance(author_a, Tag):
            href = author_a.attrs.get("href", "")
            href = _sanitize_href(href)

        author = author.text
        title = title.text
        date = date.text
        m = Message(author, title, date, href, unread, hasAttachment)
        msgs.append(m)
    return msgs


def get_max_page_number(client: Client) -> int:
    """
    Retrieves the maximum page number of messages.

    Args:
        client (Client): The client object for making HTTP requests.

    Returns:
        int: The maximum page number.
    """
    soup = no_access_check(BeautifulSoup(client.get(client.MESSAGE_URL).text, "lxml"))
    try:
        pages = soup.select_one("div.pagination > span")
        if not pages:
            return 0
        max_pages = pages.text.replace("\xa0", "")
        max_pages_re = re.search("z[0-9]*", max_pages)
        if max_pages_re is None:
            return 0
        max_pages_number = int(max_pages_re.group(0).replace("z", ""))
    except:
        raise ParseError("Error while trying to get max page number.")
    return max_pages_number - 1


def get_received(client: Client, page: int) -> List[Message]:
    """
    Retrieves received messages from a specific page.

    Args:
        client (Client): The client object for making HTTP requests.
        page (int): The page number of messages to retrieve.

    Returns:
        List[Message]: A list of received Message objects.
    """
    payload = {
        "numer_strony105": page,
        "porcjowanie_pojemnik105": "105",
    }
    response = client.post(client.MESSAGE_URL, data=payload)
    soup = no_access_check(BeautifulSoup(response.text, "lxml"))
    received_msgs = parse(soup)
    return received_msgs


def get_sent(client: Client, page: int) -> List[Message]:
    """
    Retrieves sent messages from a specific page.

    Args:
        client (Client): The client object for making HTTP requests.
        page (int): The page number of messages to retrieve.

    Returns:
        List[Message]: A list of sent Message objects.
    """
    payload = {
        "numer_strony105": page,
        "porcjowanie_pojemnik105": "105",
    }
    response = client.post(client.SEND_MESSAGE_URL, data=payload)
    soup = no_access_check(BeautifulSoup(response.text, "lxml"))
    received_msgs = parse_sent(soup)
    return received_msgs
