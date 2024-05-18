# type: ignore[attr-defined]
"""
# Librus Synergia web scraper.

## General usage
```python
from librus_apix.client import new_client, Client, Token

# First thing we create a new client which can be done with new_client func
client: Client = new_client() # this creates a Client with default urls and empty Token

# Now we update the token with client.get_token(u, p)
_token: Token = client.get_token(username, password) # this sets and returns token attribute

# Now that we have our token updated we can work on saving it. This can be done by extracting the key.
# A key is a combination of 2 authorization cookies Librus uses. Format: '{DZIENNIKSID:SDZIENNIKSID}'
key = client.token.API_Key # can be also done with str(client.token)

# A token can be then created from such key or DZIENNIKSID/SDZIENNIKSID cookies
token = Token(API_Key=key)

# or with cookie values
token = Token(dzienniksid=d_id, sdzienniksid=sd_id)

# The token can then be just passed into new_client function
client = new_client(token=token)

# Now that we have our client ready we can pass it into any modules function like so:
from librus_apix.announcements import get_announcements, Announcement
announcements: list[Announcement] = get_announcements(client)
...

# If you think of hosting this on any kind of VPS, etc. You might want to setup yourself
# some kind of proxy, as librus tends to randomly block all known VPN, VPS ip addresses.
# This has nothing to do with with the library,
# they just happen to do it randomly for few hours at a time.

# Now you can pass proxy into your client
proxy={"http": "http://my-proxy.xyz"}
# with new_client()
client = new_client(proxy=proxy)
# with Client()
client = Client(proxy=proxy)
# or just pass it into your existing client
client.proxy = proxy
```

### in further docs you will find AI slop. Be sure to report any inconsistencies in issues!
"""

from importlib import metadata as importlib_metadata


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()
