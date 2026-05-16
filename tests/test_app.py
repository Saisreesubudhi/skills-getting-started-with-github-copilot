import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


# Preserve original activities so tests can reset global state between runs
ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: restore the activities state before each test
    app_module.activities = copy.deepcopy(ORIGINAL_ACTIVITIES)
    yield


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_get_activities(client):
    # Arrange (fixture)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data


def test_signup_new_participant(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in app_module.activities[activity]["participants"]
    assert app_module.activities[activity]["participants"].count(email) == 1


def test_signup_duplicate_participant(client):
    # Arrange
    activity = "Chess Club"
    existing = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={existing}")

    # Assert
    assert response.status_code == 400
    assert app_module.activities[activity]["participants"].count(existing) == 1


def test_unregister_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "daniel@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert response.status_code == 200
    assert email not in app_module.activities[activity]["participants"]


def test_unregister_nonexistent_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "notfound@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert response.status_code == 404
