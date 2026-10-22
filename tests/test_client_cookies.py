"""Cookie isolation tests using real sessions and an in-memory HTTP transport."""

import json
from email.message import Message
from http.cookies import SimpleCookie
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

import pytest
from requests import Response
from requests.adapters import BaseAdapter
from requests.cookies import RequestsCookieJar, extract_cookies_to_jar

from librus_apix.client import Client, Token, new_client


def request_cookies(request):
    cookies = SimpleCookie(request.headers.get("Cookie", ""))
    return {name: cookie.value for name, cookie in cookies.items()}


class LoginTransport(BaseAdapter):
    """Serve synthetic login responses without replacing session cookie handling."""

    def __init__(self):
        self.account = ""
        self.requests = []

    def send(self, request, **kwargs):
        self.requests.append(request)
        path = urlsplit(request.url).path
        if request.method == "POST" and path.endswith("/OAuth/Authorization"):
            self.account = parse_qs(request.body)["login"][0]

        headers = Message()
        if path.endswith("/Authorization/2FA"):
            for name in ("DZIENNIKSID", "SDZIENNIKSID", "LOGIN_CONTEXT"):
                headers.add_header(
                    "Set-Cookie",
                    f"{name}={self.account}; Domain=.librus.pl; Path=/",
                )
        elif path.endswith("/refreshToken"):
            headers.add_header("Set-Cookie", "oauth_token=synthetic-oauth; Path=/")

        response = Response()
        response.status_code = 200
        response.url = request.url
        response.request = request
        response._content = json.dumps(
            {"status": "ok", "cookies": request_cookies(request)}
        ).encode()
        response.raw = SimpleNamespace(_original_response=SimpleNamespace(msg=headers))
        extract_cookies_to_jar(response.cookies, request, response.raw)
        return response

    def close(self):
        pass


def attach_transport(client):
    transport = LoginTransport()
    client._session.mount("https://", transport)
    client._session.mount("http://", transport)
    return transport


@pytest.mark.parametrize("factory", [lambda: Client(Token()), new_client])
def test_default_clients_do_not_share_cookies(factory):
    first = factory()
    second = factory()

    first.cookies.set("ACCOUNT_CONTEXT", "first-account")

    assert second.cookies.get("ACCOUNT_CONTEXT") is None


@pytest.mark.parametrize("initial_cookies", [{}, {"EXISTING": "caller-value"}])
def test_explicit_cookie_jar_is_preserved(initial_cookies):
    jar = RequestsCookieJar()
    jar.update(initial_cookies)
    client = Client(Token(), extra_cookies=jar)
    attach_transport(client)

    client.get_token("account-a", "synthetic-password")
    result = client.get(client.MESSAGE_URL).json()["cookies"]

    assert client.cookies is jar
    assert result.get("LOGIN_CONTEXT") == "account-a"
    assert jar.get("LOGIN_CONTEXT") == "account-a"
    if initial_cookies:
        assert result["EXISTING"] == "caller-value"


@pytest.mark.parametrize("method", ["get", "post", "post_json", "refresh_oauth"])
def test_login_cookies_are_sent_on_followup_requests(method):
    client = new_client()
    transport = attach_transport(client)
    client.get_token("account-a", "synthetic-password")

    if method == "get":
        client.get(client.MESSAGE_URL)
    elif method == "post":
        client.post(client.MESSAGE_URL, {"action": "list"})
    elif method == "post_json":
        client.post_json(client.MESSAGE_URL, {"action": "list"})
    else:
        assert client.refresh_oauth() == "synthetic-oauth"

    cookies = request_cookies(transport.requests[-1])
    assert cookies.get("LOGIN_CONTEXT") == "account-a"
    assert cookies["DZIENNIKSID"] == "account-a"
    assert cookies["SDZIENNIKSID"] == "account-a"


def test_interleaved_requests_keep_account_cookies_separate():
    first = new_client()
    second = new_client()
    attach_transport(first)
    attach_transport(second)
    first.get_token("account-a", "synthetic-password")
    first.cookies.set("ACCOUNT_CONTEXT", "account-a")
    second.get_token("account-b", "synthetic-password")
    second.cookies.set("ACCOUNT_CONTEXT", "account-b")

    for client, account in [
        (first, "account-a"),
        (second, "account-b"),
        (first, "account-a"),
    ]:
        cookies = client.get(client.MESSAGE_URL).json()["cookies"]
        assert cookies["ACCOUNT_CONTEXT"] == account
        assert cookies["LOGIN_CONTEXT"] == account
        assert cookies["DZIENNIKSID"] == account
        assert cookies["SDZIENNIKSID"] == account
