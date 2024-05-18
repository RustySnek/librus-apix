Module librus_apix.grades
=========================
This module defines functions and data classes for retrieving and managing grade-related data from the Librus API.

Classes:
    - Gpa: Represents the semestral grade for a specific semester and subject.
    - Grade: Represents a single grade entry with detailed information.
    - GradeDescriptive: Represents a descriptive grade entry with detailed information.

Functions:
    - get_grades: Fetches and returns the grades, semestral averages, and descriptive grades from Librus.

Usage:
```python
from librus_apix.grades import get_grades

try:
    # Fetch grades data
    numeric_grades, average_grades, descriptive_grades = get_grades(client, sort_by="all")
    # Process the grades data as required
    ...
except ArgumentError as e:
    # Handle invalid argument error
    ...
except ParseError as e:
    # Handle parse error
    ...
```

Functions
---------

    
`get_grades(client: librus_apix.client.Client, sort_by: str = 'all') ‑> Tuple[List[DefaultDict[str, List[librus_apix.grades.Grade]]], DefaultDict[str, List[librus_apix.grades.Gpa]], List[DefaultDict[str, List[librus_apix.grades.GradeDescriptive]]]]`
:   Fetches and returns the grades, semestral averages and descriptive grades from librus.
    
    Args:
        client (Client): The client object used to interact with the server.
        sort_by (str): The criteria to sort grades. Can be 'all', 'week', or 'last_login'.
    
    Returns:
        Tuple: A tuple containing lists of numeric and descriptive grades, and GPA information.
    
    Raises:
        ArgumentError: If an invalid sort_by value is provided.
        ParseError: If there is an error in parsing the grades.

Classes
-------

`Gpa(semester: int, gpa: float | str, subject: str)`
:   Represents the Semestral Grade for a specific semester and subject.
    
    Attributes:
        semester (int): The semester number (e.g., 1 for first semester, 2 for second semester).
        gpa (float | str): The GPA value, which can be a float or a "-" string meaning it's empty.
        subject (str): The subject for which the GPA is calculated.

    ### Class variables

    `gpa: float | str`
    :

    `semester: int`
    :

    `subject: str`
    :

`Grade(title: str, grade: str, counts: bool, date: str, href: str, desc: str, semester: int, category: str, teacher: str, weight: int)`
:   Represents a single grade entry with detailed information.
    
    Attributes:
        title (str): The title of the grade.
        grade (str): The grade string value (e.g., '2', '4+', etc.).
        value (float): Property function. Returns calculated float of grade. (e.g., '4.5 for 4+', '2.75 for 3-')
        counts (bool): Indicates whether the grade counts towards the GPA.
        date (str): The date when the grade was given.
        href (str): A URL suffix associated with the grade.
        desc (str): A detailed description of the grade.
        semester (int): The semester number (e.g., 1 for first semester, 2 for second semester).
        category (str): The category of the grade (e.g., 'Homework', 'Exam').
        teacher (str): The name of the teacher who gave the grade.
        weight (int): The weight of the grade in calculating the final score.

    ### Class variables

    `category: str`
    :

    `counts: bool`
    :

    `date: str`
    :

    `desc: str`
    :

    `grade: str`
    :

    `href: str`
    :

    `semester: int`
    :

    `teacher: str`
    :

    `title: str`
    :

    `weight: int`
    :

    ### Instance variables

    `value: float | str`
    :   Calculates and returns the numeric value of the grade based on its string representation.
        
        Returns:
            Union[float, str]: The numeric value of the grade or a string indicating it doesn't count.
        Raises:
            ValueError: if grade's format is invalid ex. A+, B+ instead of 5+, 4+

`GradeDescriptive(title: str, grade: str, date: str, href: str, desc: str, semester: int, teacher: str)`
:   GradeDescriptive(title: str, grade: str, date: str, href: str, desc: str, semester: int, teacher: str)

    ### Class variables

    `date: str`
    :

    `desc: str`
    :

    `grade: str`
    :

    `href: str`
    :

    `semester: int`
    :

    `teacher: str`
    :

    `title: str`
    :