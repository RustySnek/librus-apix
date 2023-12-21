from librus_apix.student_information import get_student_information
from librus_apix.get_token import get_token

username = "USERNAME"
password = "PASSWORD"
token = get_token(username, password)

info = get_student_information(token)

"""
class StudentInformation:
    name: str
    class_name: str
    number: int
    tutor: str
    school: dict
    lucky_number: int | str
"""

# Print out current lucky number and class' tutor
print(info.tutor,info.lucky_number)
