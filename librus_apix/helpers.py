from bs4 import BeautifulSoup
from librus_apix.exceptions import TokenError
import re


def no_access_check(soup: BeautifulSoup):
    pattern = "Brak dostępu"
    no_access = soup.select_one("#page h2.inside")
    if pattern in no_access.get_text():
        raise TokenError("Malformed or expired token.")
    else:
        return soup
