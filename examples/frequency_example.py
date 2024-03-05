from librus_apix.attendance import get_attendance_frequency
from librus_apix.get_token import get_token

username = "USERNAME"
password = "PASSWORD"
token = get_token(username, password)

frequency = get_attendance_frequency(token) # first_sem, second_sem, overall_freq
print(frequency)

