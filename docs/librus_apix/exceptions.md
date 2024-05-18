Module librus_apix.exceptions
=============================
This module defines custom exception classes used in the Librus API interactions for handling various error scenarios.

Exceptions:
    - TokenKeyError: Raised when there is an issue with the API token key.
    - ArgumentError: Raised when an invalid argument is provided to a function.
    - TokenError: Raised for errors related to API token management.
    - AuthorizationError: Raised when there is an authorization error during API access.
    - ParseError: Raised when there is an error parsing data.
    - DateError: Raised for errors related to date handling.
    - MaintananceError: Raised when the API is under maintenance.

Classes
-------

`ArgumentError(*args, **kwargs)`
:   Common base class for all non-exit exceptions.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`AuthorizationError(*args, **kwargs)`
:   Common base class for all non-exit exceptions.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`DateError(*args, **kwargs)`
:   Common base class for all non-exit exceptions.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`MaintananceError(*args, **kwargs)`
:   Common base class for all non-exit exceptions.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`ParseError(*args, **kwargs)`
:   Common base class for all non-exit exceptions.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`TokenError(*args, **kwargs)`
:   Common base class for all non-exit exceptions.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`TokenKeyError(*args, **kwargs)`
:   Common base class for all non-exit exceptions.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException