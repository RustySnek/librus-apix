from bs4 import BeautifulSoup
from librus_apix.exceptions import TokenError


def no_access_check(soup: BeautifulSoup):
    if soup.text.strip() == "Brak dostępu":
        raise TokenError("Malformed or expired token.")
    else:
        return soup
