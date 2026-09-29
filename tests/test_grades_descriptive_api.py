"""Offline tests for new-schema descriptive grades loaded from the gateway API.
All data is synthetic."""

import pytest
from requests.exceptions import ConnectionError, HTTPError

import librus_apix.urls as urls
from librus_apix.client import Client, Token
from librus_apix.grades import get_grades

STUDENT = "LID-AUTH-USER-STUDENT"
GRADES_URL = urls.GATEWAY_API_DESCRIPTIVE_GRADES + STUDENT

PAGE = """
<html><body>
<table class="decorated stretch newSchemaGradesByStudentTable"><tbody>
  <tr class="studentRow line0" data-user_id="1" data-subject_id="11">
    <td class="micro center screen-only"></td><td>Przedmiot 1</td>
    <td class="gradesCell" data-semester="1"></td><td class="gradesCell" data-semester="2"></td>
  </tr>
  <tr class="studentRow line1" data-user_id="1" data-subject_id="12">
    <td class="micro center screen-only"></td><td>Przedmiot 2</td>
    <td class="gradesCell" data-semester="1"></td><td class="gradesCell" data-semester="2"></td>
  </tr>
</tbody></table>
<table class="decorated stretch">
  <tr class="line0">
    <td class="center micro screen-only"></td><td>Przedmiot 1</td><td>Brak ocen</td><td></td>
    <td class="center"> - </td><td>Brak ocen</td><td></td><td class="center"> - </td>
    <td></td><td class="center"> - </td>
  </tr>
</table>
</body></html>
"""


def grade(**kw):
    item = {
        "subjectId": "LID-S1",
        "teacherId": "LID-T1",
        "addedBy": "LID-T1",
        "area": {"name": "Komunikacja"},
        "scaleValue": {"value": "6"},
        "content": "Treść 1",
        "comments": "Komentarz 1",
        "date": "2026-09-22",
        "semester": 1,
    }
    item.update(kw)
    return item


def routes():
    return {
        urls.GATEWAY_API_TOKEN_INFO: {"UserType": 5, "UserIdentifier": "LID-AUTH-USER-PARENT"},
        urls.GATEWAY_API_USER_INFO + "LID-AUTH-USER-PARENT": {
            "IdentifierOfStudentAssignedWithUser": STUDENT
        },
        GRADES_URL: {
            "data": [
                grade(),
                grade(subjectId="LID-S2", semester=2, scaleValue=None, comments=None),
                grade(subjectId="LID-S3"),
                grade(semester=0),
            ]
        },
        urls.GATEWAY_API_SUBJECTS: {
            "data": [
                {"identifier": "LID-S1", "numericIdentifier": 11, "name": "API 1"},
                {"identifier": "LID-S2", "numericIdentifier": 12, "name": "API 2"},
                {"identifier": "LID-S3", "numericIdentifier": 13, "name": "Przedmiot 3"},
            ]
        },
        urls.GATEWAY_API_USERS: {
            "Users": [{"AccountId": "LID-T1", "FirstName": "1", "LastName": "Nauczyciel"}]
        },
    }


class Resp:
    def __init__(self, payload=None, status=200, text=""):
        self.payload, self.status_code, self.text = payload, status, text

    def json(self):
        if self.payload is None:
            raise ValueError("not json")
        return self.payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise HTTPError(self.status_code)


class FakeClient(Client):
    def __init__(self, page=PAGE, routes=None):
        super().__init__(Token(API_Key="x:y"))
        self.page, self.routes, self.calls = page, routes or {}, []

    def _answer(self, url):
        answer = self.routes.get(url)
        if isinstance(answer, Exception):
            raise answer
        return answer if isinstance(answer, Resp) else Resp(answer, 200 if answer else 404)

    def refresh_oauth(self):
        self.calls.append(self.REFRESH_URL)
        return "oauth"

    def post(self, url, data):
        self.calls.append(url)
        return Resp(text=self.page)

    def post_json(self, url, data=None):
        self.calls.append(url)
        return self._answer(url)

    def get(self, url):
        self.calls.append(url)
        return self._answer(url)


def test_new_schema_grades_loaded_from_api():
    client = FakeClient(routes=routes())
    grades, averages, descriptive = get_grades(client)

    g = descriptive[0]["Przedmiot 1"][0]  # subject name taken from the page
    assert (g.title, g.grade, g.date, g.semester, g.teacher, g.href) == (
        "Przedmiot 1", "6", "2026-09-22", 1, "Nauczyciel 1", "",
    )
    assert "Obszar: Komunikacja" in g.desc and "Komentarz: Komentarz 1" in g.desc
    assert descriptive[1]["Przedmiot 2"][0].grade == "OO"  # no scale value, like the page
    assert descriptive[0]["Przedmiot 3"][0].grade == "6"  # subject not on the page
    assert sum(len(v) for sem in descriptive for v in sem.values()) == 3  # semester 0 skipped
    assert GRADES_URL in client.calls
    assert "Przedmiot 1" in grades[0] and "Przedmiot 1" in averages


def test_old_schema_does_not_call_api():
    page = PAGE.replace("newSchemaGradesByStudentTable", "")
    client = FakeClient(page=page, routes=routes())
    get_grades(client)
    assert client.calls == [client.GRADES_URL]


@pytest.mark.parametrize(
    "url, answer",
    [
        (GRADES_URL, Resp(status=500)),
        (GRADES_URL, ConnectionError()),
        (GRADES_URL, Resp(text="<html>")),
        (urls.GATEWAY_API_TOKEN_INFO, None),
        (urls.GATEWAY_API_SUBJECTS, {"data": ["unexpected"]}),
        (urls.GATEWAY_API_USERS, {"Users": {"unexpected": 1}}),
    ],
)
def test_api_problems_do_not_break_get_grades(url, answer):
    r = routes()
    r[url] = answer
    grades, _, descriptive = get_grades(FakeClient(routes=r))
    assert "Przedmiot 1" in grades[0]
    assert not any(v for sem in descriptive for v in sem.values())


def test_post_json_sends_json(monkeypatch):
    sent = {}

    def fake_post(self, url, **kwargs):
        sent.update(kwargs, url=url, headers=dict(self.headers))
        return Resp({})

    monkeypatch.setattr("requests.Session.post", fake_post)
    Client(Token(API_Key="a:b")).post_json(GRADES_URL)
    assert sent["url"] == GRADES_URL
    assert sent["json"] == {}
    assert sent["headers"]["Content-Type"] == "application/json"
