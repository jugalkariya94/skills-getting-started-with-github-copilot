"""
Integration tests for FastAPI endpoints using AAA (Arrange-Act-Assert) pattern.
Tests verify correct behavior for all HTTP endpoints with success and error scenarios.
"""
import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Test suite for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        ARRANGE: Activities are loaded from fixtures
        ACT: Send GET request to /activities
        ASSERT: Response contains all activities with correct structure
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        assert activities["Chess Club"]["max_participants"] == 12
        assert len(activities["Chess Club"]["participants"]) == 2

    def test_get_activities_includes_all_required_fields(self, client):
        """
        ARRANGE: Activities are loaded from fixtures
        ACT: Send GET request to /activities
        ASSERT: Each activity has required fields
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_student_successfully(self, client):
        """
        ARRANGE: Student email and activity name are ready
        ACT: Send POST request to signup endpoint
        ASSERT: Response confirms signup and participant list is updated
        """
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity}"
        # Verify participant was added
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()[activity]
        assert email in updated_activity["participants"]

    def test_signup_duplicate_student_returns_error(self, client):
        """
        ARRANGE: Student is already signed up for activity
        ACT: Send POST request to signup same student
        ASSERT: Response returns 400 error with appropriate message
        """
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        ARRANGE: Activity does not exist
        ACT: Send POST request to nonexistent activity
        ASSERT: Response returns 404 error
        """
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_multiple_students_to_same_activity(self, client):
        """
        ARRANGE: Multiple different students ready to sign up
        ACT: Sign up three different students to same activity
        ASSERT: All three are added successfully
        """
        # Arrange
        students = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
        activity = "Programming Class"

        # Act & Assert
        for student in students:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": student}
            )
            assert response.status_code == 200

        # Verify all were added
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()[activity]
        for student in students:
            assert student in updated_activity["participants"]


class TestUnregister:
    """Test suite for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_existing_student_successfully(self, client):
        """
        ARRANGE: Student is registered for activity
        ACT: Send DELETE request to unregister
        ASSERT: Student is removed from participant list
        """
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity}"
        # Verify participant was removed
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()[activity]
        assert email not in updated_activity["participants"]

    def test_unregister_nonexistent_student_returns_error(self, client):
        """
        ARRANGE: Student is not registered for activity
        ACT: Send DELETE request to unregister
        ASSERT: Response returns 400 error
        """
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()

    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """
        ARRANGE: Activity does not exist
        ACT: Send DELETE request to nonexistent activity
        ASSERT: Response returns 404 error
        """
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_multiple_students_from_activity(self, client):
        """
        ARRANGE: Multiple students are registered for activity
        ACT: Unregister each student one by one
        ASSERT: Each is successfully removed
        """
        # Arrange
        students = ["michael@mergington.edu", "daniel@mergington.edu"]
        activity = "Chess Club"

        # Act & Assert
        for student in students:
            response = client.delete(
                f"/activities/{activity}/unregister",
                params={"email": student}
            )
            assert response.status_code == 200

        # Verify all were removed
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()[activity]
        assert len(updated_activity["participants"]) == 0
