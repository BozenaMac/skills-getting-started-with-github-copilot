"""Tests for the Mergington High School API."""

from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestRoot:
    def test_root_redirect(self):
        # Arrange
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivities:
    def test_get_activities(self):
        # Arrange
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_activity_structure(self):
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity in activities.values():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)


class TestSignup:
    def test_signup_for_activity(self):
        # Arrange
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for Chess Club"

    def test_signup_duplicate(self):
        # Arrange
        email = "duplicate@mergington.edu"
        client.post("/activities/Chess Club/signup", params={"email": email})

        # Act
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_nonexistent_activity(self):
        # Arrange
        email = "test@mergington.edu"

        # Act
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRemoveParticipant:
    def test_remove_participant(self):
        # Arrange
        email = "removeme@mergington.edu"
        client.post("/activities/Art Club/signup", params={"email": email})

        # Act
        response = client.delete(
            "/activities/Art Club/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from Art Club"

    def test_remove_nonexistent_participant(self):
        # Arrange
        email = "missing@mergington.edu"

        # Act
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_remove_from_nonexistent_activity(self):
        # Arrange
        email = "test@mergington.edu"

        # Act
        response = client.delete(
            "/activities/Unknown Club/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
