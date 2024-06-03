"""

This module provides classes and functions for managing API tokens, handling HTTP operations, and creating client instances for interacting with the Librus API.

Classes:
    - Token: A class to manage and store API tokens.
    - Client: A class to handle HTTP operations using tokens.

Functions:
    - new_client: Function to create a new instance of the Client class.

Usage:
```python
my_client: Client = new_client()
_token: Token = my_client.get_token(username, password) # update the client token


#Alternatively, you can use the classes directly:
my_token = Token(API_Key="your_api_key")
my_client = Client(token=my_token)
```
"""

from typing import Dict, Optional

from requests import Session
from requests.models import Response
from requests.sessions import RequestsCookieJar
from requests.utils import cookiejar_from_dict, dict_from_cookiejar

import librus_apix.urls as urls
from librus_apix.exceptions import AuthorizationError, MaintananceError, TokenKeyError


class Token:
    """
     A class to manage and store API tokens.

    The API key should be formatted as "{DZIENNIKSID}:{SDZIENNIKSID}".

    Attributes:
        API_Key (str): The combined API key.
        csrf_token (str): CSRF token for the session.
        oauth (str): OAuth token for the session.

    Methods:
        _parse_api_key(API_Key: str) -> dict:
            Parses the API key and returns a dictionary with the tokens used for cookies.
        Raises:
            TokenKeyError: If the API_Key is not in the correct format.
    """

    def __init__(
        self,
        API_Key: Optional[str] = None,
        dzienniks: Optional[str] = None,
        sdzienniks: Optional[str] = None,
    ):
        """
        Initializes the Token object with the given API key or token parts.

        Args:
            API_Key (str, optional): The API key in the format 'DZIENNIKSID:SDZIENNIKSID'. Defaults to None.
            dzienniks (str, optional): The first part of the API key. Defaults to None / Ignored if API_Key is passed.
            sdzienniks (str, optional): The second part of the API key. Defaults to None / Ignored if API_Key is passed.
        """
        if API_Key:
            key = API_Key
        elif dzienniks and sdzienniks:
            key = f"{dzienniks}:{sdzienniks}"
        else:
            key = ""

        self.API_Key = key
        self.csrf_token = ""
        self.oauth = ""

    def __repr__(self) -> str:
        """
        Returns a string representation of the API Key.

        Returns:
            str: A string representation of the API Key.
        """
        return self.API_Key

    def _parse_api_key(self, API_Key: str) -> dict:
        """
        Parses the API Key string into a dictionary.

        The API Key string should be in the format 'DZIENNIKSID:SDZIENNIKSID'.

        Args:
            API_Key (str): The API Key string to be parsed.

        Returns:
            dict: A dictionary containing the parsed API Key, with keys 'DZIENNIKSID' and 'SDZIENNIKSID'.

        Raises:
            TokenKeyError: If the API Key is not in the correct format.
        """
        parts = API_Key.split(":")
        if len(parts) != 2:
            raise TokenKeyError(
                "API_Key must be in the format 'DZIENNIKSID:SDZIENNIKSID'"
            )
        return {"DZIENNIKSID": parts[0], "SDZIENNIKSID": parts[1]}

    def access_cookies(self) -> RequestsCookieJar:
        """
        returns CookieJar containing authorization cookies.

        Returns:
            RequestsCookieJar: A CookieJar containing the authorization cookies generated from the parsed API Key.
        """
        return cookiejar_from_dict(self._parse_api_key(self.API_Key))


class Client:
    """
    A class to handle HTTP operations using the tokens.

    Attributes:
        token (Token): The Token object containing the API key and tokens.
        proxy (dict): The proxy settings for the session.
        BASE_URL (str): The base URL for the site.
        API_URL (str): The API URL.
        GRADES_URL (str): The URL for grades.
        TIMETABLE_URL (str): The URL for the timetable.
        ANNOUNCEMENTS_URL (str): The URL for announcements.
        MESSAGE_URL (str): The URL for messages.
        SEND_MESSAGE_URL (str): The URL for sending messages.
        ATTENDANCE_URL (str): The URL for attendance.
        ATTENDANCE_DETAILS_URL (str): The URL for attendance details.
        SCHEDULE_URL (str): The URL for the schedule.
        HOMEWORK_URL (str): The URL for homework.
        HOMEWORK_DETAILS_URL (str): The URL for homework details.
        INFO_URL (str): The URL for information.
        COMPLETED_LESSONS_URL (str): The URL for completed lessons.
        GATEWAY_API_ATTENDANCE (str): The URL for gateway API attendance.
        RECIPIENTS_URL (str): The URL for recipients.
        RECIPIENT_GROUPS_URL (str): The URL for recipient groups.
        INDEX_URL (str): Url for student index
        cookies (RequestsCookieJar): additional cookies
        _session (Session): The requests session for making HTTP calls.

    Methods:
        refresh_oauth() -> str:
            Refreshes the OAuth token then returns it.
        post(url: str, data: Dict[str, str]) -> Response:
            Makes a POST request to the specified URL with the given data.
        get(url: str) -> Response:
            Makes a GET request to the specified URL.
    """

    def __init__(
        self,
        token: Token,
        base_url: str = urls.BASE_URL,
        api_url: str = urls.API_URL,
        grades_url: str = urls.GRADES_URL,
        timetable_url: str = urls.TIMETABLE_URL,
        announcements_url: str = urls.ANNOUNCEMENTS_URL,
        message_url: str = urls.MESSAGE_URL,
        send_message_url: str = urls.SEND_MESSAGE_URL,
        attendance_url: str = urls.ATTENDANCE_URL,
        attendance_details_url: str = urls.ATTENDANCE_DETAILS_URL,
        schedule_url: str = urls.SCHEDULE_URL,
        recent_schedule_url: str = urls.RECENT_SCHEDULE_URL,
        homework_url: str = urls.HOMEWORK_URL,
        homework_details_url: str = urls.HOMEWORK_DETAILS_URL,
        info_url: str = urls.INFO_URL,
        recipients_url: str = urls.RECIPIENTS_URL,
        recipient_groups_url: str = urls.RECIPIENT_GROUPS_URL,
        completed_lessons_url: str = urls.COMPLETED_LESSONS_URL,
        gateway_api_attendance: str = urls.GATEWAY_API_ATTENDANCE,
        refresh_oauth_url: str = urls.REFRESH_OAUTH_URL,
        index_url: str = urls.INDEX_URL,
        proxy: Dict[str, str] = {},
        extra_cookies: RequestsCookieJar = RequestsCookieJar(),
    ):
        self.token = token
        self.proxy = proxy
        self.BASE_URL = base_url
        self.API_URL = api_url
        self.GRADES_URL = grades_url
        self.TIMETABLE_URL = timetable_url
        self.ANNOUNCEMENTS_URL = announcements_url
        self.MESSAGE_URL = message_url
        self.SEND_MESSAGE_URL = send_message_url
        self.ATTENDANCE_URL = attendance_url
        self.ATTENDANCE_DETAILS_URL = attendance_details_url
        self.SCHEDULE_URL = schedule_url
        self.RECENT_SCHEDULE_URL = recent_schedule_url
        self.HOMEWORK_URL = homework_url
        self.HOMEWORK_DETAILS_URL = homework_details_url
        self.INFO_URL = info_url
        self.COMPLETED_LESSONS_URL = completed_lessons_url
        self.GATEWAY_API_ATTENDANCE = gateway_api_attendance
        self.RECIPIENTS_URL = recipients_url
        self.RECIPIENT_GROUPS_URL = recipient_groups_url
        self.REFRESH_URL = refresh_oauth_url
        self.INDEX_URL = index_url
        self.cookies = extra_cookies
        self._session = Session()
        """
        Initializes a new instance of Client.

        Args:
            token (Token): The authentication token required for API access.
            base_url (str, optional): The base URL of the API. Defaults to urls.BASE_URL.
            api_url (str, optional): The URL of the API endpoint. Defaults to urls.API_URL.
            grades_url (str, optional): The URL of the grades endpoint. Defaults to urls.GRADES_URL.
            timetable_url (str, optional): The URL of the timetable endpoint. Defaults to urls.TIMETABLE_URL.
            announcements_url (str, optional): The URL of the announcements endpoint. Defaults to urls.ANNOUNCEMENTS_URL.
            message_url (str, optional): The URL of the message endpoint. Defaults to urls.MESSAGE_URL.
            send_message_url (str, optional): The URL of the send message endpoint. Defaults to urls.SEND_MESSAGE_URL.
            attendance_url (str, optional): The URL of the attendance endpoint. Defaults to urls.ATTENDANCE_URL.
            attendance_details_url (str, optional): The URL of the attendance details endpoint. Defaults to urls.ATTENDANCE_DETAILS_URL.
            schedule_url (str, optional): The URL of the schedule endpoint. Defaults to urls.SCHEDULE_URL.
            homework_url (str, optional): The URL of the homework endpoint. Defaults to urls.HOMEWORK_URL.
            homework_details_url (str, optional): The URL of the homework details endpoint. Defaults to urls.HOMEWORK_DETAILS_URL.
            info_url (str, optional): The URL of the info endpoint. Defaults to urls.INFO_URL.
            recipients_url (str, optional): The URL of the recipients endpoint. Defaults to urls.RECIPIENTS_URL.
            recipient_groups_url (str, optional): The URL of the recipient groups endpoint. Defaults to urls.RECIPIENT_GROUPS_URL.
            completed_lessons_url (str, optional): The URL of the completed lessons endpoint. Defaults to urls.COMPLETED_LESSONS_URL.
            gateway_api_attendance (str, optional): The URL of the gateway API attendance endpoint. Defaults to urls.GATEWAY_API_ATTENDANCE.
            refresh_oauth_url (str, optional): The URL of the refresh OAuth endpoint. Defaults to urls.REFRESH_OAUTH_URL.
            proxy (Dict[str, str], optional): A dictionary containing proxy settings. Defaults to an empty dictionary.
         """

    def get_token(
        self,
        username: str,
        password: str,
    ) -> Token:
        """
        Retrieves an authentication Token class for the provided username and password.

        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.

        Returns:
            Token: An authentication token containing 'DZIENNIKSID' and 'SDZIENNIKSID' cookies.

        Raises:
            MaintananceError: If the API returns a maintenance status code or message.
            AuthorizationError: If there is an error during the authorization process.
        """
        with self._session as s:
            s.headers = urls.HEADERS
            maint_check = s.get(self.API_URL, proxies=self.proxy)
            if maint_check.status_code == 503:
                message_list = maint_check.json().get("Message")
                if not message_list:
                    # during recent maintenance there were no messages (empty list)
                    raise MaintananceError("maintenance")
                raise MaintananceError(message_list[0]["description"])
            s.get(
                self.API_URL
                + "/OAuth/Authorization?client_id=46&response_type=code&scope=mydata",
                proxies=self.proxy,
            )
            response = s.post(
                self.API_URL + "/OAuth/Authorization?client_id=46",
                data={"action": "login", "login": username, "pass": password},
                proxies=self.proxy,
            )
            if response.json()["status"] == "error":
                raise AuthorizationError(response.json()["errors"][0]["message"])

            s.get(self.API_URL + response.json().get("goTo"), proxies=self.proxy)

            cookies: Dict = dict_from_cookiejar(s.cookies)
            dzienniks = cookies.get("DZIENNIKSID")
            sdzienniks = cookies.get("SDZIENNIKSID")
            if dzienniks is None or sdzienniks is None:
                raise AuthorizationError("Authorization cookies were not found")

            token = Token(dzienniks=dzienniks, sdzienniks=sdzienniks)
            self.token = token
            return token

    def refresh_oauth(self) -> str:
        """
        Refreshes the OAuth token.

        Returns:
            str: The new OAuth token.

        Raises:
            AuthorizationError: If the token cannot be refreshed.
        """
        self.cookies.update(self.token.access_cookies())
        with self._session as s:
            s.headers = urls.HEADERS
            s.cookies = self.cookies
            response: Response = s.get(self.REFRESH_URL, proxies=self.proxy)
            if response.status_code == 200:
                oauth = response.cookies.get("oauth_token")
                self.token.oauth = oauth
                return oauth
        raise AuthorizationError(
            f"Error while refreshing oauth token {response.content}"
        )

    def post(self, url: str, data: Dict[str, str]) -> Response:
        """
        Makes a POST request to the specified URL with the given data.

        Args:
            url (str): The URL to send the POST request to.
            data (Dict[str, Union[str, int]]): The data to include in the POST request.

        Returns:
            Response: The response from the server.
        """
        self.cookies.update(self.token.access_cookies())
        with self._session as s:
            s.headers = urls.HEADERS
            s.cookies = self.cookies
            response: Response = s.post(url, data=data, proxies=self.proxy)
            return response

    def get(self, url: str) -> Response:
        """
        Makes a GET request to the specified URL.

        Args:
            url (str): The URL to send the GET request to.

        Returns:
            Response: The response from the server.
        """
        self.cookies.update(self.token.access_cookies())
        with self._session as s:
            s.headers = urls.HEADERS
            s.cookies = self.cookies
            response: Response = s.get(url, proxies=self.proxy)
            return response


def new_client(
    token: Token = Token(),
    base_url: str = urls.BASE_URL,
    api_url: str = urls.API_URL,
    grades_url: str = urls.GRADES_URL,
    timetable_url: str = urls.TIMETABLE_URL,
    announcements_url: str = urls.ANNOUNCEMENTS_URL,
    message_url: str = urls.MESSAGE_URL,
    send_message_url: str = urls.SEND_MESSAGE_URL,
    attendance_url: str = urls.ATTENDANCE_URL,
    attendance_details_url: str = urls.ATTENDANCE_DETAILS_URL,
    schedule_url: str = urls.SCHEDULE_URL,
    recent_schedule_url: str = urls.RECENT_SCHEDULE_URL,
    homework_url: str = urls.HOMEWORK_URL,
    homework_details_url: str = urls.HOMEWORK_DETAILS_URL,
    info_url: str = urls.INFO_URL,
    recipients_url: str = urls.RECIPIENTS_URL,
    recipient_groups_url: str = urls.RECIPIENT_GROUPS_URL,
    completed_lessons_url: str = urls.COMPLETED_LESSONS_URL,
    gateway_api_attendance: str = urls.GATEWAY_API_ATTENDANCE,
    refresh_oauth_url: str = urls.REFRESH_OAUTH_URL,
    index_url: str = urls.INDEX_URL,
    proxy: dict[str, str] = {},
):
    """
    Creates a new instance of the Client class.

    Args:
        token (Optional[Token], optional): The authentication token. Defaults to None.
        base_url (str, optional): The base URL of the API. Defaults to urls.BASE_URL.
        api_url (str, optional): The URL of the API endpoint. Defaults to urls.API_URL.
        grades_url (str, optional): The URL of the grades endpoint. Defaults to urls.GRADES_URL.
        timetable_url (str, optional): The URL of the timetable endpoint. Defaults to urls.TIMETABLE_URL.
        announcements_url (str, optional): The URL of the announcements endpoint. Defaults to urls.ANNOUNCEMENTS_URL.
        message_url (str, optional): The URL of the message endpoint. Defaults to urls.MESSAGE_URL.
        send_message_url (str, optional): The URL of the send message endpoint. Defaults to urls.SEND_MESSAGE_URL.
        attendance_url (str, optional): The URL of the attendance endpoint. Defaults to urls.ATTENDANCE_URL.
        attendance_details_url (str, optional): The URL of the attendance details endpoint. Defaults to urls.ATTENDANCE_DETAILS_URL.
        schedule_url (str, optional): The URL of the schedule endpoint. Defaults to urls.SCHEDULE_URL.
        homework_url (str, optional): The URL of the homework endpoint. Defaults to urls.HOMEWORK_URL.
        homework_details_url (str, optional): The URL of the homework details endpoint. Defaults to urls.HOMEWORK_DETAILS_URL.
        info_url (str, optional): The URL of the info endpoint. Defaults to urls.INFO_URL.
        recipients_url (str, optional): The URL of the recipients endpoint. Defaults to urls.RECIPIENTS_URL.
        recipient_groups_url (str, optional): The URL of the recipient groups endpoint. Defaults to urls.RECIPIENT_GROUPS_URL.
        completed_lessons_url (str, optional): The URL of the completed lessons endpoint. Defaults to urls.COMPLETED_LESSONS_URL.
        gateway_api_attendance (str, optional): The URL of the gateway API attendance endpoint. Defaults to urls.GATEWAY_API_ATTENDANCE.
        refresh_oauth_url (str, optional): The URL of the refresh OAuth endpoint. Defaults to urls.REFRESH_OAUTH_URL.
        index_url (str, optional): The url for student index
        proxy (dict[str, str], optional): A dictionary containing proxy settings. Defaults to an empty dictionary.

    Returns:
        Client: A new instance of the Client class.
    """
    if not isinstance(token, Token):
        token = Token()
    return Client(
        token,
        base_url,
        api_url,
        grades_url,
        timetable_url,
        announcements_url,
        message_url,
        send_message_url,
        attendance_url,
        attendance_details_url,
        schedule_url,
        recent_schedule_url,
        homework_url,
        homework_details_url,
        info_url,
        recipients_url,
        recipient_groups_url,
        completed_lessons_url,
        gateway_api_attendance,
        refresh_oauth_url,
        index_url,
        proxy,
    )
