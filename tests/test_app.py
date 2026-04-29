from src.app import activities


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_count = len(activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == expected_count
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "student1@mergington.edu"
    original_participants = list(activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == len(original_participants) + 1


def test_signup_for_nonexistent_activity_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student2@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_duplicate_signup_returns_400(client):
    # Arrange
    activity_name = "Programming Class"
    email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_custom_activity_increases_participant_count(client):
    # Arrange
    activity_name = "Tiny Activity"
    activities[activity_name] = {
        "description": "A tiny activity for custom signup testing",
        "schedule": "Mondays, 1:00 PM",
        "max_participants": 1,
        "participants": ["current@mergington.edu"]
    }
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == 2


def test_unregister_from_activity_removes_participant(client):
    # Arrange
    activity_name = "Gym Class"
    email = activities[activity_name]["participants"][0]
    original_participants = list(activities[activity_name]["participants"])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == len(original_participants) - 1


def test_unregister_nonexistent_activity_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student3@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_missing_participant_returns_404(client):
    # Arrange
    activity_name = "Drama Club"
    email = "missingstudent@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_full_signup_and_unregister_flow(client):
    # Arrange
    activity_name = "Science Club"
    email = "journey@mergington.edu"

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    activities_response = client.get("/activities")
    unregister_response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    final_activities_response = client.get("/activities")

    # Assert
    assert signup_response.status_code == 200
    assert activities_response.status_code == 200
    assert email in activities_response.json()[activity_name]["participants"]
    assert unregister_response.status_code == 200
    assert final_activities_response.status_code == 200
    assert email not in final_activities_response.json()[activity_name]["participants"]
