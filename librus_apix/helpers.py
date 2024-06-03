"""
This module defines a function for checking access to Librus resources by examining the content of a BeautifulSoup object.

Functions:
    - no_access_check: Checks for access to Librus resources by examining the content of a BeautifulSoup object.

"""

from bs4 import BeautifulSoup
from librus_apix.exceptions import TokenError


def no_access_check(soup: BeautifulSoup) -> BeautifulSoup:
    pattern = "Brak dostępu"
    no_access = soup.select_one("h2.inside")
    if not no_access:
        return soup
    if pattern in no_access.get_text():
        raise TokenError("Malformed or expired token.")
    else:
        return soup
