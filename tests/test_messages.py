import pytest
from librus_apix.messages import Message, get_recieved, get_sent, get_max_page_number

def test_get_grades(token):
    max_page = get_max_page_number(token)
    assert isinstance(max_page, int)
    recieved = get_recieved(token, max_page)
    assert isinstance(recieved, list)
    assert all(isinstance(msg, Message) for msg in recieved)
    sent = get_sent(token, max_page)
    assert isinstance(sent, list)
    assert all(isinstance(msg, Message) for msg in sent)
