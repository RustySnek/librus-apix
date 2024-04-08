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
        base_url: Optional[str] = urls.BASE_URL,
        api_url: Optional[str] = urls.API_URL,
        grades_url: Optional[str] = urls.GRADES_URL,
        timetable_url: Optional[str] = urls.TIMETABLE_URL,
        announcements_url: Optional[str] = urls.ANNOUNCEMENTS_URL,
        message_url: Optional[str] = urls.MESSAGE_URL,
        attendance_url: Optional[str] = urls.ATTENDANCE_URL,
        attendance_details_url: Optional[str] = urls.ATTENDANCE_DETAILS_URL,
        schedule_url: Optional[str] = urls.SCHEDULE_URL,
        homework_url: Optional[str] = urls.HOMEWORK_URL,
        homework_details_url: Optional[str] = urls.HOMEWORK_DETAILS_URL,
        info_url: Optional[str] = urls.INFO_URL,
        completed_lessons_url: Optional[str] = urls.COMPLETED_LESSONS_URL,
        gateway_api_attendance: Optional[str] = urls.GATEWAY_API_ATTENDANCE,
        proxy: Optional[dict[str, str]] = {}
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
        self.proxy = proxy
        self.oauth = ""
        self.BASE_URL = base_url
        self.API_URL = api_url
        self.GRADES_URL = grades_url
        self.TIMETABLE_URL = timetable_url
        self.ANNOUNCEMENTS_URL = announcements_url
        self.MESSAGE_URL = message_url
        self.ATTENDANCE_URL = attendance_url
        self.ATTENDANCE_DETAILS_URL = attendance_details_url
        self.SCHEDULE_URL = schedule_url
        self.HOMEWORK_URL = homework_url
        self.HOMEWORK_DETAILS_URL = homework_details_url
        self.INFO_URL = info_url
        self.COMPLETED_LESSONS_URL = completed_lessons_url
        self.GATEWAY_API_ATTENDANCE = gateway_api_attendance

    def refresh_oauth(self) -> str:
        with self._session as s:
            s.headers = urls.HEADERS
            s.cookies = cookiejar_from_dict(self.cookies)
            response: Response = s.get("https://synergia.librus.pl/refreshToken", proxies=self.proxy)
            if response.status_code == 200:
                oauth = response.cookies.get("oauth_token")
                self.oauth = oauth
                return oauth
        raise AuthorizationError(f"Error while refreshing oauth token {response.content}")

    def post(self, url: str, data: Dict[str, Union[str, int]]) -> Response:
        with self._session as s:
            s.headers = urls.HEADERS
            s.cookies = cookiejar_from_dict(self.cookies)
            response: Response = s.post(url, json=data, proxies=self.proxy)
            return response

    def get(self, url: str) -> Response:
        with self._session as s:
            s.headers = urls.HEADERS
            s.cookies = cookiejar_from_dict(self.cookies)
            response: Response = s.get(url, proxies=self.proxy)
            return response


def get_token(
    username: str,
    password: str,
    base_url: Optional[str] = urls.BASE_URL,
    api_url: str = urls.API_URL,
    grades_url: Optional[str] = urls.GRADES_URL,
    timetable_url: Optional[str] = urls.TIMETABLE_URL,
    announcements_url: Optional[str] = urls.ANNOUNCEMENTS_URL,
    message_url: Optional[str] = urls.MESSAGE_URL,
    attendance_url: Optional[str] = urls.ATTENDANCE_URL,
    attendance_details_url: Optional[str] = urls.ATTENDANCE_DETAILS_URL,
    schedule_url: Optional[str] = urls.SCHEDULE_URL,
    homework_url: Optional[str] = urls.HOMEWORK_URL,
    homework_details_url: Optional[str] = urls.HOMEWORK_DETAILS_URL,
    info_url: Optional[str] = urls.INFO_URL,
    completed_lessons_url: Optional[str] = urls.COMPLETED_LESSONS_URL,
    gateway_api_attendance: Optional[str] = urls.GATEWAY_API_ATTENDANCE,
    proxy: Optional[dict[str, str]] = {},
) -> Token:
    with Session() as s:
        s.headers = urls.HEADERS
        maint_check = s.get(api_url, proxies=proxy)
        if maint_check.status_code == 503:
            message_list = maint_check.json().get("Message")
            if not message_list:
                # during recent maintenance there were no messages (empty list)
                raise MaintananceError("maintenance")
            raise MaintananceError(message_list[0]["description"])
        s.get(
            api_url
            + "/OAuth/Authorization?client_id=46&response_type=code&scope=mydata", proxies=proxy
        )
        response = s.post(
            api_url + "/OAuth/Authorization?client_id=46",
            data={"action": "login", "login": username, "pass": password}, proxies=proxy
        )
        if response.json()["status"] == "error":
            raise AuthorizationError(response.json()["errors"][0]["message"])

        s.get(api_url + response.json().get("goTo"), proxies=proxy)

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
            gateway_api_attendance,
            proxy=proxy
        )

        return token
