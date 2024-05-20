Module librus_apix.client
=========================
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

Functions
---------

    
`new_client(token: librus_apix.client.Token = , base_url: str = 'https://synergia.librus.pl', api_url: str = 'https://api.librus.pl', grades_url: str = 'https://synergia.librus.pl/przegladaj_oceny/uczen', timetable_url: str = 'https://synergia.librus.pl/przegladaj_plan_lekcji', announcements_url: str = 'https://synergia.librus.pl/ogloszenia', message_url: str = 'https://synergia.librus.pl/wiadomosci/1/5', send_message_url: str = 'https://synergia.librus.pl/wiadomosci/1/6', attendance_url: str = 'https://synergia.librus.pl/przegladaj_nb/uczen', attendance_details_url: str = 'https://synergia.librus.pl/przegladaj_nb/szczegoly/', schedule_url: str = 'https://synergia.librus.pl/terminarz/', homework_url: str = 'https://synergia.librus.pl/moje_zadania', homework_details_url: str = 'https://synergia.librus.pl/moje_zadania/podglad/', info_url: str = 'https://synergia.librus.pl/informacja', recipients_url: str = 'https://synergia.librus.pl/getRecipients', recipient_groups_url: str = 'https://synergia.librus.pl/wiadomosci/2/6', completed_lessons_url: str = 'https://synergia.librus.pl/zrealizowane_lekcje', gateway_api_attendance: str = 'https://synergia.librus.pl/gateway/api/2.0/Attendances', refresh_oauth_url: str = 'https://synergia.librus.pl/refreshToken', index_url: str = 'https://synergia.librus.pl/uczen/index', proxy: dict[str, str] = {})`
:   Creates a new instance of the Client class.
    
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

Classes
-------

`Client(token: librus_apix.client.Token, base_url: str = 'https://synergia.librus.pl', api_url: str = 'https://api.librus.pl', grades_url: str = 'https://synergia.librus.pl/przegladaj_oceny/uczen', timetable_url: str = 'https://synergia.librus.pl/przegladaj_plan_lekcji', announcements_url: str = 'https://synergia.librus.pl/ogloszenia', message_url: str = 'https://synergia.librus.pl/wiadomosci/1/5', send_message_url: str = 'https://synergia.librus.pl/wiadomosci/1/6', attendance_url: str = 'https://synergia.librus.pl/przegladaj_nb/uczen', attendance_details_url: str = 'https://synergia.librus.pl/przegladaj_nb/szczegoly/', schedule_url: str = 'https://synergia.librus.pl/terminarz/', homework_url: str = 'https://synergia.librus.pl/moje_zadania', homework_details_url: str = 'https://synergia.librus.pl/moje_zadania/podglad/', info_url: str = 'https://synergia.librus.pl/informacja', recipients_url: str = 'https://synergia.librus.pl/getRecipients', recipient_groups_url: str = 'https://synergia.librus.pl/wiadomosci/2/6', completed_lessons_url: str = 'https://synergia.librus.pl/zrealizowane_lekcje', gateway_api_attendance: str = 'https://synergia.librus.pl/gateway/api/2.0/Attendances', refresh_oauth_url: str = 'https://synergia.librus.pl/refreshToken', index_url: str = 'https://synergia.librus.pl/uczen/index', proxy: Dict[str, str] = {}, extra_cookies: requests.cookies.RequestsCookieJar = <RequestsCookieJar[]>)`
:   A class to handle HTTP operations using the tokens.
    
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

    ### Methods

    `get(self, url: str) ‑> requests.models.Response`
    :   Makes a GET request to the specified URL.
        
        Args:
            url (str): The URL to send the GET request to.
        
        Returns:
            Response: The response from the server.

    `get_token(self, username: str, password: str) ‑> librus_apix.client.Token`
    :   Retrieves an authentication Token class for the provided username and password.
        
        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.
        
        Returns:
            Token: An authentication token containing 'DZIENNIKSID' and 'SDZIENNIKSID' cookies.
        
        Raises:
            MaintananceError: If the API returns a maintenance status code or message.
            AuthorizationError: If there is an error during the authorization process.

    `post(self, url: str, data: Dict[str, str]) ‑> requests.models.Response`
    :   Makes a POST request to the specified URL with the given data.
        
        Args:
            url (str): The URL to send the POST request to.
            data (Dict[str, Union[str, int]]): The data to include in the POST request.
        
        Returns:
            Response: The response from the server.

    `refresh_oauth(self) ‑> str`
    :   Refreshes the OAuth token.
        
        Returns:
            str: The new OAuth token.
        
        Raises:
            AuthorizationError: If the token cannot be refreshed.

`Token(API_Key: Optional[str] = None, dzienniks: Optional[str] = None, sdzienniks: Optional[str] = None)`
:   A class to manage and store API tokens.
    
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
    
    Initializes the Token object with the given API key or token parts.
    
    Args:
        API_Key (str, optional): The API key in the format 'DZIENNIKSID:SDZIENNIKSID'. Defaults to None.
        dzienniks (str, optional): The first part of the API key. Defaults to None / Ignored if API_Key is passed.
        sdzienniks (str, optional): The second part of the API key. Defaults to None / Ignored if API_Key is passed.

    ### Methods

    `access_cookies(self) ‑> requests.cookies.RequestsCookieJar`
    :   returns CookieJar containing authorization cookies.
        
        Returns:
            RequestsCookieJar: A CookieJar containing the authorization cookies generated from the parsed API Key.