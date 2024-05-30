"""
Constants:
    ```python
    - HEADERS: A dictionary containing HTTP headers for making requests.
    - BASE_URL: The base URL for the Librus website.
    - API_URL: The base URL for the Librus API.
    - INDEX_URL: Student Index url
    - GRADES_URL: URL for accessing grades.
    - TIMETABLE_URL: URL for accessing the timetable.
    - ANNOUNCEMENTS_URL: URL for accessing announcements.
    - MESSAGE_URL: URL for accessing messages.
    - RECIPIENT_GROUPS_URL: URL for retrieving recipient groups for messages.
    - RECIPIENTS_URL: URL for retrieving recipients for messages.
    - SEND_MESSAGE_URL: URL for sending messages.
    - ATTENDANCE_URL: URL for accessing attendance information.
    - ATTENDANCE_DETAILS_URL: URL for accessing detailed attendance information.
    - SCHEDULE_URL: URL for accessing the schedule.
    - HOMEWORK_URL: URL for accessing homework.
    - HOMEWORK_DETAILS_URL: URL for accessing detailed homework information.
    - INFO_URL: URL for accessing information.
    - COMPLETED_LESSONS_URL: URL for accessing completed lessons.
    - GATEWAY_API_ATTENDANCE: URL for accessing attendance data via the gateway API.
    - REFRESH_OAUTH_URL: URL for refreshing OAuth tokens.
    ```
"""

from typing import Dict, Union

HEADERS: Dict[str, Union[str, bytes]] = {
    "User-Agent": "Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0",
    "Content-Type": "application/x-www-form-urlencoded",
}
BASE_URL = "https://synergia.librus.pl"
API_URL = "https://api.librus.pl"
INDEX_URL = BASE_URL + "/uczen/index"
GRADES_URL = BASE_URL + "/przegladaj_oceny/uczen"
TIMETABLE_URL = f"{BASE_URL}/przegladaj_plan_lekcji"
ANNOUNCEMENTS_URL = f"{BASE_URL}/ogloszenia"
MESSAGE_URL = f"{BASE_URL}/wiadomosci/1/5"
RECIPIENT_GROUPS_URL = f"{BASE_URL}/wiadomosci/2/6"
RECIPIENTS_URL = f"{BASE_URL}/getRecipients"
SEND_MESSAGE_URL = f"{BASE_URL}/wiadomosci/1/6"
ATTENDANCE_URL = f"{BASE_URL}/przegladaj_nb/uczen"
ATTENDANCE_DETAILS_URL = f"{BASE_URL}/przegladaj_nb/szczegoly/"
SCHEDULE_URL = f"{BASE_URL}/terminarz/"
RECENT_SCHEDULE_URL = f"{BASE_URL}/terminarz/dodane_od_ostatniego_logowania"
HOMEWORK_URL = f"{BASE_URL}/moje_zadania"
HOMEWORK_DETAILS_URL = f"{BASE_URL}/moje_zadania/podglad/"
INFO_URL = f"{BASE_URL}/informacja"
COMPLETED_LESSONS_URL = f"{BASE_URL}/zrealizowane_lekcje"
GATEWAY_API_ATTENDANCE = f"{BASE_URL}/gateway/api/2.0/Attendances"
REFRESH_OAUTH_URL = f"{BASE_URL}/refreshToken"
