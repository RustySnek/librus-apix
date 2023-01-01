from bs4 import BeautifulSoup
from librus_apix.exceptions import TokenError
import re

def no_access_check(soup: BeautifulSoup):
    no_access = re.search('Brak dostępu', soup.text)
    if no_access:
        raise TokenError("Malformed or expired token.")
    else:
        return soup
