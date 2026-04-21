"""
API Tests for Mergington High School Activities API.
Tests follow the AAA (Arrange-Act-Assert) pattern for clarity.
"""

import pytest


class TestRoot:
    """Tests for the root endpoint."""

    def test_root_redirects_to_index(self, client):
        """
        Test that GET / redirects to /static/index.html
        
        Arrange: No setup needed for redirect test
        Act: Make GET request to /
        Assert: Verify 307 redirect status code
        """
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, mock_activities):
        """
        Test that GET /activities returns all activities with correct structure.
        
        Arrange: Use mock_activities fixture with sample data
        Act: Make GET request to /activities
        Assert: Verify response contains all activities with correct fields
        """
        # Arrange
        expected_activity_count = len(mock_activities)
        expected_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == expected_activity_count
        
        # Verify each activity has correct structure
        for activity_name, activity_details in data.items():
            assert activity_name in mock_activities
            assert set(activity_details.keys()) == expected_fields
            assert isinstance(activity_details["participants"], list)
            assert isinstance(activity_details["max_participants"], int)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client, mock_activities):
        """
        Test successful signup of a new participant.
        
        Arrange: Prepare activity name and new email
        Act: Make POST request to signup
        Assert: Verify 200 response, participant added, message correct
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "new_student@mergington.edu"
        initial_count = len(mock_activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in mock_activities[activity_name]["participants"]
        assert len(mock_activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_activity_not_found(self, client):
        """
        Test signup fails when activity does not exist.
        
        Arrange: Use non-existent activity name
        Act: Make POST request with invalid activity
        Assert: Verify 404 status and appropriate error message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_already_registered(self, client, mock_activities):
        """
        Test signup fails when student is already registered.
        
        Arrange: Use an activity and email already in participants
        Act: Make POST request to signup with same email twice
        Assert: Verify 400 status and "already signed up" error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        initial_count = len(mock_activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"
        # Verify no duplicate was added
        assert len(mock_activities[activity_name]["participants"]) == initial_count

    def test_signup_activity_full(self, client, mock_activities):
        """
        Test signup fails when activity is at max capacity.
        
        Arrange: Fill an activity to max participants
        Act: Try to add one more participant
        Assert: Verify 400 status and "activity is full" error
        """
        # Arrange
        activity_name = "Basketball Team"
        max_participants = mock_activities[activity_name]["max_participants"]
        
        # Fill the activity to capacity
        for i in range(max_participants):
            mock_activities[activity_name]["participants"].append(f"student{i}@mergington.edu")
        
        email = "no_space@mergington.edu"
        initial_count = len(mock_activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Activity is full"
        # Verify participant was not added
        assert len(mock_activities[activity_name]["participants"]) == initial_count


class TestUnregisterFromActivity:
    """Tests for the POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client, mock_activities):
        """
        Test successful unregistration of a participant.
        
        Arrange: Use an activity and registered participant
        Act: Make POST request to unregister
        Assert: Verify 200 response, participant removed, message correct
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        initial_count = len(mock_activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        assert email not in mock_activities[activity_name]["participants"]
        assert len(mock_activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_activity_not_found(self, client):
        """
        Test unregister fails when activity does not exist.
        
        Arrange: Use non-existent activity name
        Act: Make POST request with invalid activity
        Assert: Verify 404 status and appropriate error message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_registered(self, client, mock_activities):
        """
        Test unregister fails when student is not registered.
        
        Arrange: Use an activity and email not in participants
        Act: Make POST request to unregister non-enrolled student
        Assert: Verify 400 status and "not registered" error
        """
        # Arrange
        activity_name = "Basketball Team"  # Initially empty
        email = "not_registered@mergington.edu"
        initial_count = len(mock_activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not registered for this activity"
        # Verify no changes to participants
        assert len(mock_activities[activity_name]["participants"]) == initial_count


class TestIntegrationSignupAndUnregister:
    """Integration tests for signup and unregister workflow."""

    def test_signup_then_unregister_flow(self, client, mock_activities):
        """
        Test complete signup and unregister flow.
        
        Arrange: Prepare activity and new email
        Act: Sign up, verify added; then unregister, verify removed
        Assert: Verify state changes at each step
        """
        # Arrange
        activity_name = "Soccer Club"
        email = "diego@mergington.edu"
        initial_count = len(mock_activities[activity_name]["participants"])

        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert - Sign up successful
        assert signup_response.status_code == 200
        assert email in mock_activities[activity_name]["participants"]
        assert len(mock_activities[activity_name]["participants"]) == initial_count + 1

        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert - Unregister successful
        assert unregister_response.status_code == 200
        assert email not in mock_activities[activity_name]["participants"]
        assert len(mock_activities[activity_name]["participants"]) == initial_count
