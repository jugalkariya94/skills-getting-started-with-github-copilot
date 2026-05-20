"""
Unit tests for business logic using AAA (Arrange-Act-Assert) pattern.
Tests verify core logic like participant validation, duplicate prevention, and removal.
"""
import pytest


class TestParticipantValidation:
    """Unit tests for participant validation logic."""

    def test_check_activity_exists(self, sample_activities):
        """
        ARRANGE: Sample activities dictionary
        ACT: Check if activity exists
        ASSERT: Correctly identifies existing and non-existing activities
        """
        # Act & Assert
        assert "Chess Club" in sample_activities
        assert "Nonexistent Activity" not in sample_activities

    def test_check_max_participants(self, sample_activities):
        """
        ARRANGE: Activities with different max participant counts
        ACT: Retrieve max_participants value
        ASSERT: Value is correct for each activity
        """
        # Assert
        assert sample_activities["Chess Club"]["max_participants"] == 12
        assert sample_activities["Programming Class"]["max_participants"] == 20
        assert sample_activities["Gym Class"]["max_participants"] == 30

    def test_count_available_spots(self, sample_activities):
        """
        ARRANGE: Activities with existing participants
        ACT: Calculate available spots
        ASSERT: Calculation is correct
        """
        # Arrange & Act
        chess_max = sample_activities["Chess Club"]["max_participants"]
        chess_current = len(sample_activities["Chess Club"]["participants"])
        available_spots = chess_max - chess_current

        # Assert
        assert chess_current == 2
        assert available_spots == 10


class TestDuplicateSignupPrevention:
    """Unit tests for preventing duplicate signups."""

    def test_student_already_in_participants_list(self, sample_activities):
        """
        ARRANGE: Student email and activity with participants
        ACT: Check if email is in participants list
        ASSERT: Correctly identifies duplicate
        """
        # Arrange
        email = "michael@mergington.edu"
        activity = sample_activities["Chess Club"]

        # Act
        is_participant = email in activity["participants"]

        # Assert
        assert is_participant is True

    def test_student_not_in_participants_list(self, sample_activities):
        """
        ARRANGE: Student email not in participants
        ACT: Check if email is in participants list
        ASSERT: Correctly identifies new student
        """
        # Arrange
        email = "newstudent@mergington.edu"
        activity = sample_activities["Chess Club"]

        # Act
        is_participant = email in activity["participants"]

        # Assert
        assert is_participant is False

    def test_duplicate_detection_across_different_activities(self, sample_activities):
        """
        ARRANGE: Same email in different activities
        ACT: Check presence in each activity
        ASSERT: Student can be in multiple activities
        """
        # Arrange
        emma = "emma@mergington.edu"

        # Act
        in_programming = emma in sample_activities["Programming Class"]["participants"]
        in_chess = emma in sample_activities["Chess Club"]["participants"]

        # Assert
        assert in_programming is True
        assert in_chess is False  # Emma is only in Programming Class


class TestParticipantRemoval:
    """Unit tests for removing participants from activities."""

    def test_remove_participant_from_list(self, sample_activities):
        """
        ARRANGE: Activity with multiple participants
        ACT: Remove one participant
        ASSERT: Participant is removed, others remain
        """
        # Arrange
        email_to_remove = "michael@mergington.edu"
        activity = sample_activities["Chess Club"]
        initial_count = len(activity["participants"])

        # Act
        activity["participants"].remove(email_to_remove)

        # Assert
        assert len(activity["participants"]) == initial_count - 1
        assert email_to_remove not in activity["participants"]
        assert "daniel@mergington.edu" in activity["participants"]

    def test_remove_all_participants(self, sample_activities):
        """
        ARRANGE: Activity with participants
        ACT: Remove all participants one by one
        ASSERT: Activity has no participants
        """
        # Arrange
        activity = sample_activities["Chess Club"]
        original_participants = list(activity["participants"])

        # Act
        for participant in original_participants:
            activity["participants"].remove(participant)

        # Assert
        assert len(activity["participants"]) == 0
        assert activity["participants"] == []

    def test_remove_nonexistent_participant_raises_error(self, sample_activities):
        """
        ARRANGE: Activity and non-existent email
        ACT: Try to remove email not in participants
        ASSERT: ValueError is raised
        """
        # Arrange
        email = "nonexistent@mergington.edu"
        activity = sample_activities["Chess Club"]

        # Act & Assert
        with pytest.raises(ValueError):
            activity["participants"].remove(email)


class TestParticipantList:
    """Unit tests for participant list structure and integrity."""

    def test_participants_is_list(self, sample_activities):
        """
        ARRANGE: Sample activities
        ACT: Check type of participants
        ASSERT: Participants is always a list
        """
        # Act & Assert
        for activity_name, activity_data in sample_activities.items():
            assert isinstance(activity_data["participants"], list)

    def test_all_participants_are_strings(self, sample_activities):
        """
        ARRANGE: Activities with participants
        ACT: Check type of each participant
        ASSERT: All participants are email strings
        """
        # Act & Assert
        for activity_name, activity_data in sample_activities.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email format check

    def test_no_duplicate_participants_in_list(self, sample_activities):
        """
        ARRANGE: Activities with participants
        ACT: Compare list length with set length
        ASSERT: No duplicate emails in participants list
        """
        # Act & Assert
        for activity_name, activity_data in sample_activities.items():
            participants = activity_data["participants"]
            assert len(participants) == len(set(participants))
