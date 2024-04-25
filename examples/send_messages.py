from librus_apix.messages import get_recipients, send_message
from librus_apix.get_token import get_token

username = "USERNAME"
password = "PASSWORD"
token = get_token(username, password)

"""
Available recipient groups:
            "teachers": "nauczyciel"
            "tutors": "wychowawca"
            "parent_council": "szkolna_rada_rodzicow"
            "pedagogue": "pedagog"
            "admin": "admin"
            "secretary": "sekretariat"
"""

recipients = get_recipients(token, "teachers")

"""
returns a dictionary {"fullname": "recipient_id"} like {"John Brown": "1234567"}
"""

my_recipient = recipient_id["John Brown"]
my_second_recipient = recipient_id["Barbara Brown"]
sent = send_message(token, "Message Title", "Message\n content", "teachers", [my_recipient, my_second_recipient])

"""
returns either true or false if status_code was 200
meaning most likely message was sent correctly
"""

if sent == True:
    print("message was sent")
else:
    print("There was an issue in sending your message")
