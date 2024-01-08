from bs4 import BeautifulSoup
from librus_apix.exceptions import TokenError, ParseError


def no_access_check(soup: BeautifulSoup):
    pattern = "Brak dostępu"
    no_access = soup.select_one("#page h2.inside")
    if not no_access:
        return soup
    if pattern in no_access.get_text():
        raise TokenError("Malformed or expired token.")
    else:
        return soup
