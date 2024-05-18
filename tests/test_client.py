from logging import Logger
from typing import Dict
import pytest
from requests.models import Response
from requests.sessions import RequestsCookieJar

from librus_apix.client import Client, Token


def test_client_token(client: Client, log: Logger):
    token = client.token
    assert isinstance(token, Token)
    assert isinstance(token.__repr__(), str)
    if str(token) == "":
        log.warning("test token key is empty")
        pytest.skip("Omitting token parse tests due to empty key")
    assert isinstance(token._parse_api_key(token.API_Key), Dict)
    assert isinstance(token.access_cookies(), RequestsCookieJar)


def test_get_base_url(client: Client):
    assert isinstance(client.cookies, RequestsCookieJar)
    response = client.get(client.BASE_URL)
    assert isinstance(response, Response)
    assert response.status_code == 200
