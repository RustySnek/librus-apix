"""
Compare grades with synergia.librus.pl using a real account (skipped otherwise):

    LIBRUS_LOGIN=... LIBRUS_PASSWORD=... pytest tests/test_live_grades.py
"""

import pytest

from librus_apix.client import new_client
from librus_apix.grades import get_grades


def test_live_grades(request):
    login = request.config.getoption("login")
    password = request.config.getoption("password")
    if not login or not password:
        pytest.skip("set LIBRUS_LOGIN and LIBRUS_PASSWORD (or --login/--password)")

    client = new_client()
    client.get_token(login, password)
    grades, _, descriptive = get_grades(client)

    lines = []
    for semester in (0, 1):
        lines.append(f"\n=== Okres {semester + 1} ===")
        for subject in sorted(set(grades[semester]) | set(descriptive[semester])):
            numeric = " ".join(g.grade for g in grades[semester][subject])
            lines.append(f"{subject}: {numeric or '-'}")
            for g in descriptive[semester][subject]:
                lines.append(f"    [{g.grade}] {g.date} {g.teacher}: " + g.desc.replace("\n", " | "))
    with request.config.pluginmanager.get_plugin("capturemanager").global_and_fixture_disabled():
        print("\n".join(lines))
