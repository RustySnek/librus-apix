from logging import Logger
from typing import List
import pytest
from librus_apix.client import Client
from librus_apix.messages import (
    Message,
    MessageData,
    get_received,
    get_sent,
    get_max_page_number,
    message_content,
)


def _test_message_data(msg: Message, log: Logger):
    strings = list(msg.__dict__.items())[:4]
    for key, val in strings:
        assert isinstance(val, str)
        if val == "":
            log.warning(f"{key} is an empty string")
    assert isinstance(msg.unread, bool)
    assert isinstance(msg.has_attachment, bool)


def test_get_max_page(client: Client):
    max_page = get_max_page_number(client)
    assert isinstance(max_page, int)
    assert max_page >= 0


def test_get_sent_messages(client: Client, log: Logger):
    sent = get_sent(client, 1)
    assert isinstance(sent, list)
    for msg in sent:
        assert isinstance(msg, Message)
        _test_message_data(msg, log)


@pytest.fixture
def get_received_messages(client: Client) -> List[Message]:
    received = get_received(client, 1)
    return received


def test_get_received_messages(get_received_messages: List[Message], log: Logger):
    assert isinstance(get_received_messages, List)
    for msg in get_received_messages:
        assert isinstance(msg, Message)
        _test_message_data(msg, log)


def test_message_content(
    get_received_messages: List[Message], client: Client, log: Logger
):
    if len(get_received_messages) == 0:
        pytest.skip("No messages to check")
    sample: Message = get_received_messages[0]
    data = message_content(client, sample.href)
    assert isinstance(data, MessageData)
    for key, value in data.__dict__.items():
        if value == "":
            log.warning(f"{key} value is empty")
