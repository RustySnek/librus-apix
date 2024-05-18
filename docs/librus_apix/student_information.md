Module librus_apix.student_information
======================================
This module provides functions for retrieving student information from the Librus system, parsing it, and formatting it into a structured representation.

Classes:
    - StudentInformation: Represents student information with attributes such as name, class name, student number, etc.

Functions:
    - get_student_information: Retrieves student information from Librus.

Usage:
    ```python
    from librus_apix.client import new_client

    # Create a new client instance
    client = new_client()
    client.get_token(username, password)

    # Fetch student information
    student_info = get_student_information(client)
    print(student_info.name)
    print(student_info.class_name)
    print(student_info.number)
    print(student_info.tutor)
    print(student_info.school)
    print(student_info.lucky_number)
    ```

Functions
---------

    
`get_student_information(client: librus_apix.client.Client)`
:   Retrieves student information from librus.
    
    Args:
        client (Client): The client object for making HTTP requests.
    
    Returns:
        StudentInformation: An object containing the student's information.
    
    Raises:
        ParseError: If there is an error while parsing or retrieving student information.

Classes
-------

`StudentInformation(name: str, class_name: str, number: int, tutor: str, school: str, lucky_number: Union[int, str])`
:   Represents student information.
    
    Attributes:
        name (str): The name of the student.
        class_name (str): The class name of the student.
        number (int): The student number.
        tutor (str): The tutor of the student.
        school (str): The school of the student.
        lucky_number (Union[int, str]): The lucky number of the student, if available.

    ### Class variables

    `class_name: str`
    :

    `lucky_number: Union[int, str]`
    :

    `name: str`
    :

    `number: int`
    :

    `school: str`
    :

    `tutor: str`
    :