import json
import pytest

from api import app
from .constants import (
    NEW_USER_EMAIL,
    NEW_USER_DATA,
    EXISTING_USER_EMAIL,
    EXISTING_USER_DATA,
    NON_EXISTING_USER_EMAIL,
)


def test_get_users():
    # GET /users
    # Retrieve all users
    response = app.test_client().get("/users")
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert type(res) is list
    assert type(res[0]) is dict
    assert len(res) == 996


def test_get_user():
    # GET /users/:email
    # Successful retrieval of data for a user
    response = app.test_client().get(f"/users/{EXISTING_USER_EMAIL}")
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert type(res) is dict
    # Don't include the id or events in the comparison
    res.pop("id")
    res.pop("events")
    assert res == EXISTING_USER_DATA

    # Failed attempt to retrieve the data for a non-existent email
    # GET /users/:email
    response = app.test_client().get(f"/users/{NON_EXISTING_USER_EMAIL}")
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 400
    assert res == f"User '{NON_EXISTING_USER_EMAIL}' does not exist"


def test_register_user():
    # POST /users
    # Successful registration of a new user
    response = app.test_client().post("/users", json=NEW_USER_DATA)
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert res == f"User '{NEW_USER_EMAIL}' was successfully registered"

    # GET /users/:email
    # Verify the user was successfully registered
    response = app.test_client().get(f"/users/{NEW_USER_EMAIL}")
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert type(res) is dict
    # Don't include the id or events in the comparison
    res.pop("id")
    res.pop("events")
    assert res == NEW_USER_DATA

    # POST /users/:email
    # Failed attempt to register a user with an email that already exists
    response = app.test_client().post(f"/users", json=EXISTING_USER_DATA)
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 400
    assert res == f"User '{EXISTING_USER_EMAIL}' already exists"


def test_update_user():
    UPDATE_DATA = {
        "phone": "888-888-8888",
        "skills": [
            {"skill": "Chakra UI", "rating": 1},
            {"skill": "Ruby", "rating": 2},
        ],
    }

    # PUT /users/:email
    # Successful update
    response = app.test_client().put(f"/users/{EXISTING_USER_EMAIL}", json=UPDATE_DATA)
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert res == f"User '{EXISTING_USER_EMAIL}' was successfully updated"

    # GET /users/:email
    # Verify the data was updated
    response = app.test_client().get(f"/users/{EXISTING_USER_EMAIL}")
    res = json.loads(response.data.decode("utf-8"))
    assert res.get("phone") == UPDATE_DATA.get("phone")
    assert res.get("skills") == UPDATE_DATA.get("skills")

    # PUT /users/:email
    # Failed attempt to update the data for a non-existent email
    response = app.test_client().put(
        f"/users/{NON_EXISTING_USER_EMAIL}", json=UPDATE_DATA
    )
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 400
    assert res == f"User '{NON_EXISTING_USER_EMAIL}' does not exist"


def test_delete_user():
    # PUT /users/:email
    # Successful deletion
    response = app.test_client().delete(f"/users/{NEW_USER_EMAIL}")
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert res == f"User '{NEW_USER_EMAIL}' was successfully deleted"

    # GET /users/:email
    # Verify the user was deleted
    response = app.test_client().get(f"/users/{NEW_USER_EMAIL}")
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 400
    assert res == f"User '{NEW_USER_EMAIL}' does not exist"

    # DELETE /users/:email
    # Failed attempt to delete the data for a non-existent email
    response = app.test_client().delete(f"/users/{NON_EXISTING_USER_EMAIL}")
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 400
    assert res == f"User '{NON_EXISTING_USER_EMAIL}' does not exist"


def test_update_user_to_existing_email():
    EXISTING_USER_EMAIL_2 = "lorettabrown@example.net"

    # PUT /users/:email
    # Failed attempt to update a user's email to an email that
    # is already associated with another existing user
    response = app.test_client().put(
        f"/users/{EXISTING_USER_EMAIL}", json={"email": EXISTING_USER_EMAIL_2}
    )
    res = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 400
    assert (
        res
        == f"Update failed, user with email '{EXISTING_USER_EMAIL_2}' already exists"
    )
