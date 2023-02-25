import json
import pytest

from api import app


def test_get_skills():
    # GET /skills
    # Retrieve a list of skills
    response = app.test_client().get("/skills")
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert type(res) is list
    assert type(res[0]) is dict
    assert list(res[0].keys()) == ["skill", "count"]

    # GET /skills?min_frequency=min_frequency
    # Retrieve a list of skills with min_frequency filter applied
    min_frequency = 20
    response = app.test_client().get(f"/skills?min_frequency={min_frequency}")
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    counts = [skill.get("count") for skill in res]
    assert all(count >= min_frequency for count in counts)

    # GET /skills?max_frequency=max_frequency
    # Retrieve a list of skills with max_frequency filter applied
    max_frequency = 30
    response = app.test_client().get(f"/skills?max_frequency={max_frequency}")
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    counts = [skill.get("count") for skill in res]
    assert all(count <= max_frequency for count in counts)

    # GET /skills?min_frequency=min_frequency&max_frequency=max_frequency
    # Retrieve a list of skills with min_frequency and max_frequency filters applied
    response = app.test_client().get(
        f"/skills?min_frequency={min_frequency}&max_frequency={max_frequency}"
    )
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    counts = [skill.get("count") for skill in res]
    assert all(count >= min_frequency and count <= max_frequency for count in counts)
