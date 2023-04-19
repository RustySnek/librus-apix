from librus_apix.announcements import get_announcements
from librus_apix.get_token import get_token

username = "USERNAME"
password = "PASSWORD"
token = get_token(username, password)

announcements = get_announcements(token)

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
