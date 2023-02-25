import json
import pytest

from api import app
from .constants import (
    EXISTING_USER_EMAIL,
    EXISTING_USER_EMAIL_2,
    EXISTING_USER_EMAIL_3,
    NON_EXISTING_USER_EMAIL,
    INVALID_EVENT,
)

EVENTS = json.load(open("./mock_data/events_data.json"))


def test_scan_event():
    # POST /users/events/:email
    # Successful "scanning" of user to event
    response = app.test_client().post(
        f"/users/events/{EXISTING_USER_EMAIL}", json=EVENTS[0]
    )
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert res == f"Successfully registered event to user '{EXISTING_USER_EMAIL}'"

    # POST /users/events/:email
    # Successful "scanning" of user to another event
    response = app.test_client().post(
        f"/users/events/{EXISTING_USER_EMAIL}", json=EVENTS[3]
    )
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert res == f"Successfully registered event to user '{EXISTING_USER_EMAIL}'"

    # GET /users/events/:email
    # Retrieve a list of events that a user scanned into
    response = app.test_client().get(f"/users/events/{EXISTING_USER_EMAIL}")
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert type(res) == list
    assert len(res) == 2
    assert res[0] == EVENTS[0]
    assert res[1] == EVENTS[3]

    # POST /users/events/:email
    # Failed attempt to scan a non-existing user to an event
    response = app.test_client().post(
        f"/users/events/{NON_EXISTING_USER_EMAIL}", json=EVENTS[0]
    )
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 400
    assert res == f"User '{NON_EXISTING_USER_EMAIL}' does not exist"

    # POST /users/events/:email
    # Failed attempt to scan a user to an invalid event
    response = app.test_client().post(
        f"/users/events/{EXISTING_USER_EMAIL}", json=INVALID_EVENT
    )
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 400
    assert res == "Invalid event data in body"

    # POST /users/events/:email
    # Failed attempt to scan a user to an event they already scanned into
    response = app.test_client().post(
        f"/users/events/{EXISTING_USER_EMAIL}", json=EVENTS[0]
    )
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 400
    assert res == f"User '{EXISTING_USER_EMAIL}' is already registered to event"


def test_get_events():
    # Scan users into a few more events
    app.test_client().post(f"/users/events/{EXISTING_USER_EMAIL}", json=EVENTS[1])
    app.test_client().post(f"/users/events/{EXISTING_USER_EMAIL_2}", json=EVENTS[1])
    app.test_client().post(f"/users/events/{EXISTING_USER_EMAIL_2}", json=EVENTS[6])
    app.test_client().post(f"/users/events/{EXISTING_USER_EMAIL_3}", json=EVENTS[1])

    # GET /events
    # Retrieve a list of events
    response = app.test_client().get("/events")
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert type(res) is list
    assert type(res[0]) is dict
    assert list(res[0].keys()) == ["event", "category", "count"]

    # GET /events?category=category
    # Retrieve a list of events with category filter applied
    category = "Workshop"
    response = app.test_client().get(f"/events?category={category}")
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    categories = []
    for event in res:
        c = event.get("category")
        if c not in categories:
            categories.append(c)
    # Only one category of results should have been returned
    assert categories == [category]

    # GET /events?min_frequency=min_frequency
    # Retrieve a list of events with min_frequency filter applied
    min_frequency = 1
    response = app.test_client().get(f"/events?min_frequency={min_frequency}")
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    counts = [event.get("count") for event in res]
    assert all(count >= min_frequency for count in counts)

    # GET /events?max_frequency=max_frequency
    # Retrieve a list of events with max_frequency filter applied
    max_frequency = 2
    response = app.test_client().get(f"/events?max_frequency={max_frequency}")
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    counts = [event.get("count") for event in res]
    assert all(count <= max_frequency for count in counts)

    # GET /events?min_frequency=min_frequency&max_frequency=max_frequency
    # Retrieve a list of events with min_frequency and max_frequency filters applied
    response = app.test_client().get(
        f"/events?min_frequency={min_frequency}&max_frequency={max_frequency}"
    )
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    counts = [event.get("count") for event in res]
    assert all(count >= min_frequency and count <= max_frequency for count in counts)
