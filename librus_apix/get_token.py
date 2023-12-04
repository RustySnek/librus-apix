import re
from typing import Optional, Union, Dict
from requests.models import Response
from bs4 import BeautifulSoup
from requests import Session
from requests.utils import cookiejar_from_dict, dict_from_cookiejar
from librus_apix.urls import API_URL, BASE_URL, HEADERS
from librus_apix.exceptions import AuthorizationError, MaintananceError


class Token:
    def __init__(self, API_Key: Optional[str] = None):
        self._session = Session()
        if not API_Key:
            self.cookies = ""
            self.csrf_token = ""
            return
        self.API_Key = API_Key
        cookies = {"DZIENNIKSID": API_Key.split(":")[0]}
        cookies["SDZIENNIKSID"] = API_Key.split(":")[1]
        self.cookies = cookies

    def post(self, url: str, data: Dict[str, Union[str, int]]) -> Response:
        with self._session as s:
            s.headers = HEADERS
            s.cookies = cookiejar_from_dict(self.cookies)
            response: Response = s.post(url, data)
            return response

    def get(self, url: str) -> Response:
        with self._session as s:
            s.headers = HEADERS
            s.cookies = cookiejar_from_dict(self.cookies)
            response: Response = s.get(url)
            return response


def get_token(username: str, password: str) -> Token:
    with Session() as s:
        s.headers = HEADERS
        maint_check = s.get("https://api.librus.pl/")
        if maint_check.status_code == 503:
            message_list = maint_check.json().get("Message")
            if not message_list:
                # during recent maintenance there were no messages (empty list)
                raise MaintananceError("maintenance")
            raise MaintananceError(message_list[0]["description"])
        s.get(
            API_URL
            + "/OAuth/Authorization?client_id=46&response_type=code&scope=mydata"
        )
        response = s.post(
            API_URL + "/OAuth/Authorization?client_id=46",
            data={"action": "login", "login": username, "pass": password},
        )
        if response.json()["status"] == "error":
            raise AuthorizationError(response.json()["errors"][0]["message"])

        res = s.get(API_URL + response.json().get("goTo"))
        cookies = dict_from_cookiejar(s.cookies)
        token = Token(str(cookies["DZIENNIKSID"] + ":" + cookies["SDZIENNIKSID"]))

        return token
