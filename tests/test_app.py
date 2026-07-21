import copy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_static_index_html():
    # Arrange / Act
    response = client.get("/", allow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    # Arrange / Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, dict)
    assert "Chess Club" in body
    assert "Programming Class" in body


def test_signup_for_activity_adds_new_participant():
    # Arrange
    email = "test.student@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_returns_404_for_missing_activity():
    # Arrange
    activity_name = "Nonexistent Activity"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": "test@example.com"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_activity_rejects_duplicate_participant():
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_removes_existing_student():
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_returns_404_for_missing_activity():
    # Arrange
    activity_name = "Nonexistent Activity"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": "test@example.com"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_returns_404_for_missing_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "missing@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"
