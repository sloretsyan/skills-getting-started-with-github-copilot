import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_state = copy.deepcopy(app.activities)
    yield
    app.activities.clear()
    app.activities.update(copy.deepcopy(original_state))


def test_get_activities_returns_activity_list():
    # Arrange
    expected_activities = {"Chess Club", "Gym Class"}

    # Act
    response = client.get("/activities")
    activities = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_activities.issubset(set(activities.keys()))
    assert isinstance(activities["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_new_participant():
    # Arrange
    activity_name = "Gym Class"
    email = "student@example.com"
    signup_url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    # Act
    response = client.post(signup_url)
    activities = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Programming Class"
    email = "emma@mergington.edu"
    signup_url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_unregisters_student():
    # Arrange
    activity_name = "Programming Class"
    email = "emma@mergington.edu"
    remove_url = f"/activities/{quote(activity_name)}/participants?email={quote(email)}"

    # Act
    response = client.delete(remove_url)
    activities = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]
