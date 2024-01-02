from librus_apix.messages import get_recieved, message_content
from librus_apix.get_token import get_token


def messages(token):
    # pages start from 0
    recieved = get_recieved(token, page=0)
    """
    Structure of Message class:
        class Message:
            author: str
            title: str
            date: str
            href: str
            unread: bool
            has_attachment: bool
    """
    # Printing out the content of the 10 newest recieved messages.
    for message in recieved[:11]:
        print()
        print(message.title)
        print(message.href)
        print(message_content(token, message.href))


if __name__ == "__main__":
    username = "USERNAME"
    password = "PASSWORD"

    token = get_token(username, password)

    messages(token)
