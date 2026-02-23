import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def preserve_activities():
    """Arrange: preserve module-level `activities` state for test isolation.
    Deep-copy before the test and restore after so tests do not interfere.
    """
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_get_activities_returns_all():
    # Arrange
    expected = copy.deepcopy(activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected


def test_signup_adds_participant():
    # Arrange
    activity = "Tennis Club"
    email = "new_student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    assert f"Signed up {email} for {activity}" in response.json().get("message", "")


def test_signup_existing_returns_400():
    # Arrange
    activity = "Chess Club"
    existing_email = activities[activity]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400


def test_remove_participant_removes():
    # Arrange
    activity = "Basketball Team"
    email = "james@mergington.edu"
    assert email in activities[activity]["participants"]

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_remove_nonexistent_returns_404():
    # Arrange
    activity = "Gym Class"
    email = "not_in_list@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
