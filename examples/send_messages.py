from librus_apix.messages import recipient_groups, get_recipients, send_message
from librus_apix.get_token import get_token

username = "USERNAME"
password = "PASSWORD"
token = get_token(username, password)

groups: List[str] = recipient_groups(token)

recipients: Dict[str, str] = get_recipients(token, groups[0])

my_recipient = recipient_id["John Brown"]
my_second_recipient = recipient_id["Barbara Brown"]
sent, result = send_message(token, "test", "test", [my_recipient, my_second_recipient])

"""
returns either true or false if message was sent AND the result message
meaning most likely message was sent correctly
"""

if sent == True:
    print(result)
else:
    print(result)
