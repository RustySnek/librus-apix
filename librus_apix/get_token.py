from typing import Optional, Union, Dict
from requests.models import Response
from requests import Session
from requests.utils import cookiejar_from_dict, dict_from_cookiejar
import librus_apix.urls as urls
from librus_apix.exceptions import AuthorizationError, MaintananceError


class Token:
    def __init__(
        self,
        API_Key: Optional[str] = None,
        base_url: Optional[str] = None,
        api_url: Optional[str] = None,
        grades_url: Optional[str] = None,
        timetable_url: Optional[str] = None,
        announcements_url: Optional[str] = None,
        message_url: Optional[str] = None,
        attendance_url: Optional[str] = None,
        attendance_details_url: Optional[str] = None,
        schedule_url: Optional[str] = None,
        homework_url: Optional[str] = None,
        homework_details_url: Optional[str] = None,
        info_url: Optional[str] = None,
        completed_lessons_url: Optional[str] = None,
        gateway_api_attendance: Optional[str] = None,
    ):
        self._session = Session()
        if not API_Key:
            self.cookies = {}
            self.csrf_token = ""
            return
        self.API_Key = API_Key
        cookies = {"DZIENNIKSID": API_Key.split(":")[0]}
        cookies["SDZIENNIKSID"] = API_Key.split(":")[1]
        self.cookies = cookies
        self.oauth = ""
        self.BASE_URL = base_url if base_url else urls.BASE_URL
        self.API_URL = api_url if api_url else urls.API_URL
        self.GRADES_URL = grades_url if grades_url else urls.GRADES_URL
        self.TIMETABLE_URL = timetable_url if timetable_url else urls.TIMETABLE_URL
        self.ANNOUNCEMENTS_URL = (
            announcements_url if announcements_url else urls.ANNOUNCEMENTS_URL
        )
        self.MESSAGE_URL = message_url if message_url else urls.MESSAGE_URL
        self.ATTENDANCE_URL = attendance_url if attendance_url else urls.ATTENDANCE_URL
        self.ATTENDANCE_DETAILS_URL = (
            attendance_details_url
            if attendance_details_url
            else urls.ATTENDANCE_DETAILS_URL
        )
        self.GATEWAY_API_ATTENDANCE = (
               gateway_api_attendance if gateway_api_attendance else urls.GATEWAY_API_ATTENDANCE
                )
        self.SCHEDULE_URL = schedule_url if schedule_url else urls.SCHEDULE_URL
        self.HOMEWORK_URL = homework_url if homework_url else urls.HOMEWORK_URL
        self.HOMEWORK_DETAILS_URL = (
            homework_details_url if homework_details_url else urls.HOMEWORK_DETAILS_URL
        )
        self.INFO_URL = info_url if info_url else urls.INFO_URL
        self.COMPLETED_LESSONS_URL = (
            completed_lessons_url
            if completed_lessons_url
            else urls.COMPLETED_LESSONS_URL
        )

    def refresh_oauth(self) -> str:
        with self._session as s:
            s.headers = urls.HEADERS
            s.cookies = cookiejar_from_dict(self.cookies)
            response: Response = s.get("https://synergia.librus.pl/refreshToken")
            if response.status_code == 200:
                oauth = response.cookies.get("oauth_token")
                self.oauth = oauth
                return oauth
        raise AuthorizationError(f"Error while refreshing oauth token {response.content}")

    def post(self, url: str, data: Dict[str, Union[str, int]]) -> Response:
        with self._session as s:
            s.headers = urls.HEADERS
            s.cookies = cookiejar_from_dict(self.cookies)
            response: Response = s.post(url, json=data)
            return response

    def get(self, url: str) -> Response:
        with self._session as s:
            s.headers = urls.HEADERS
            s.cookies = cookiejar_from_dict(self.cookies)
            response: Response = s.get(url)
            return response


def get_token(
    username: str,
    password: str,
    base_url: Optional[str] = None,
    api_url: str = urls.API_URL,
    grades_url: Optional[str] = None,
    timetable_url: Optional[str] = None,
    announcements_url: Optional[str] = None,
    message_url: Optional[str] = None,
    attendance_url: Optional[str] = None,
    attendance_details_url: Optional[str] = None,
    schedule_url: Optional[str] = None,
    homework_url: Optional[str] = None,
    homework_details_url: Optional[str] = None,
    info_url: Optional[str] = None,
    completed_lessons_url: Optional[str] = None,
) -> Token:
    with Session() as s:
        s.headers = urls.HEADERS
        maint_check = s.get(api_url)
        if maint_check.status_code == 503:
            message_list = maint_check.json().get("Message")
            if not message_list:
                # during recent maintenance there were no messages (empty list)
                raise MaintananceError("maintenance")
            raise MaintananceError(message_list[0]["description"])
        s.get(
            api_url
            + "/OAuth/Authorization?client_id=46&response_type=code&scope=mydata"
        )
        response = s.post(
            api_url + "/OAuth/Authorization?client_id=46",
            data={"action": "login", "login": username, "pass": password},
        )
        if response.json()["status"] == "error":
            raise AuthorizationError(response.json()["errors"][0]["message"])

        s.get(api_url + response.json().get("goTo"))

        cookies = dict_from_cookiejar(s.cookies)
        token = Token(
            str(cookies["DZIENNIKSID"] + ":" + cookies["SDZIENNIKSID"]),
            base_url,
            api_url,
            grades_url,
            timetable_url,
            announcements_url,
            message_url,
            attendance_url,
            attendance_details_url,
            schedule_url,
            homework_url,
            homework_details_url,
            info_url,
            completed_lessons_url,
        )

        return token
