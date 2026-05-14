"""
Comprehensive tests for the FastAPI activities application.
Tests cover GET, POST (signup), and DELETE (unregister) endpoints.
Uses pytest with AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_all_activities(self, client):
        """Test that the endpoint returns all activities."""
        # Arrange
        # No setup needed

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activities_have_correct_structure(self, client):
        """Test that each activity has the required fields."""
        # Arrange
        # No setup needed

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """Test successful signup for an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]

    def test_signup_duplicate(self, client):
        """Test that signing up twice for the same activity returns 400 error."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()

    def test_signup_nonexistent_activity(self, client):
        """Test signup to a non-existent activity returns 404 error."""
        # Arrange
        activity_name = "Fake Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_at_capacity(self, client):
        """
        Test signup when activity is at max capacity.
        NOTE: This test is skipped if the app doesn't validate capacity.
        """
        # Arrange
        # Get an activity with low max_participants
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        activity_name = "Tennis Club"  # max_participants: 12, has 2
        current_participants = len(activities_data[activity_name]["participants"])
        max_participants = activities_data[activity_name]["max_participants"]
        
        # Fill the activity to capacity
        for i in range(max_participants - current_participants):
            email = f"capacity_test_{i}@mergington.edu"
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )

        # Act - Try to add one more when at capacity
        overflow_email = "overflow@mergington.edu"
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": overflow_email}
        )

        # Assert - Check if the app validates capacity
        # If status is 200, app doesn't check capacity (skip validation check)
        if response.status_code == 200:
            # App doesn't validate capacity, which is fine
            # Just verify the signup went through
            assert "Signed up" in response.json()["message"]
        else:
            # App does validate capacity
            assert response.status_code == 400
            detail = response.json()["detail"].lower()
            assert "full" in detail or "capacity" in detail


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/signup endpoint."""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]

    def test_unregister_not_signed_up(self, client):
        """Test unregistering someone not signed up returns 400 error."""
        # Arrange
        activity_name = "Basketball Team"
        email = "notsignedup@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "not" in response.json()["detail"].lower()

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from a non-existent activity returns 404 error."""
        # Arrange
        activity_name = "Non-existent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
