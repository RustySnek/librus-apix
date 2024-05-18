"""
This module defines custom exception classes used in the Librus API interactions for handling various error scenarios.

Exceptions:
    - TokenKeyError: Raised when there is an issue with the API token key.
    - ArgumentError: Raised when an invalid argument is provided to a function.
    - TokenError: Raised for errors related to API token management.
    - AuthorizationError: Raised when there is an authorization error during API access.
    - ParseError: Raised when there is an error parsing data.
    - DateError: Raised for errors related to date handling.
    - MaintananceError: Raised when the API is under maintenance.
"""


class TokenKeyError(Exception):
    pass


class ArgumentError(Exception):
    pass


class TokenError(Exception):
    pass


class AuthorizationError(Exception):
    pass


class ParseError(Exception):
    pass


class DateError(Exception):
    pass


class MaintananceError(Exception):
    pass
