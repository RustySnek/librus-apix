from logging import Logger
import pytest
from librus_apix.get_token import Token
from librus_apix.messages import (
    Message,
    MessageData,
    get_recieved,
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


def test_get_max_page(token):
    max_page = get_max_page_number(token)
    assert isinstance(max_page, int)
    assert max_page >= 0


def test_get_sent_messages(token: Token, log: Logger):
    sent = get_sent(token, 1)
    assert isinstance(sent, list)
    for msg in sent:
        assert isinstance(msg, Message)
        _test_message_data(msg, log)


@pytest.fixture
def get_recieved_messages(token):
    recieved = get_recieved(token, 1)
    return recieved


def test_get_recieved_messages(get_recieved_messages, log: Logger):
    assert isinstance(get_recieved_messages, list)
    for msg in get_recieved_messages:
        assert isinstance(msg, Message)
        _test_message_data(msg, log)


def test_message_content(get_recieved_messages, token, log):
    if len(get_recieved_messages) == 0:
        pytest.skip("No messages to check")
    sample: Message = get_recieved_messages[0]
    data = message_content(token, sample.href)
    assert isinstance(data, MessageData)
    for key, value in data.__dict__.items():
        if value == "":
            log.warning(f"{key} value is empty")
