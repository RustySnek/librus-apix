from typing import List
from librus_apix.announcements import get_announcements, Announcement
from librus_apix.client import Client, Token, new_client

client: Client = new_client()
_token: Token = client.get_token("username", "password")
# token keys can be saved
key = client.token.API_Key
# and then reused
token = Token(API_Key=key)
client: Client = new_client(token=token)

announcements: List[Announcement] = get_announcements(client)

"""
Structure of Announcement class:
    class Announcement:
        title: str
        author: str
        description: str
        date: str
"""

# Printing out all of the announcements.
for a in announcements:
    print(f"{a.description}\n{a.author} - {a.date}\n")
