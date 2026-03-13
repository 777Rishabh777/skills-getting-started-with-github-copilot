"""
Tests for the Mergington High School Activities API.
Uses the AAA (Arrange-Act-Assert) pattern throughout.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities participants list before each test to ensure isolation."""
    original_participants = {name: list(data["participants"]) for name, data in activities.items()}
    yield
    for name, participants_list in original_participants.items():
        activities[name]["participants"] = participants_list


@pytest.fixture
def client():
    return TestClient(app)


# --- GET /activities ---

class TestGetActivities:
    def test_returns_all_activities(self, client):
        # Arrange: client is ready

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_activities_have_required_fields(self, client):
        # Arrange: client is ready

        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        for name, details in data.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details


# --- POST /activities/{activity_name}/signup ---

class TestSignupForActivity:
    def test_successful_signup(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_signup_returns_confirmation_message(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Underwater Basket Weaving"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404

    def test_duplicate_signup_returns_400(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # already a participant

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()


# --- DELETE /activities/{activity_name}/unregister ---

class TestUnregisterFromActivity:
    def test_successful_unregister(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # already a participant

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]

    def test_unregister_returns_confirmation_message(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Assert
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Underwater Basket Weaving"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Assert
        assert response.status_code == 404

    def test_unregister_non_participant_returns_400(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
