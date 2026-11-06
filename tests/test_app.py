from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import activities, app


BASE_ACTIVITIES = deepcopy(activities)
client = TestClient(app)


def reset_activities():
    activities.clear()
    activities.update(deepcopy(BASE_ACTIVITIES))


def test_get_activities_returns_expected_activity_list():
    reset_activities()

    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    expected = {
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Swimming Club",
        "Art Studio",
        "Drama Club",
        "Debate Team",
        "Science Club",
    }
    assert set(data) == expected


def test_signup_adds_student_and_blocks_duplicate_signups():
    reset_activities()
    email = "newstudent@mergington.edu"

    signup_response = client.post(f"/activities/Basketball Team/signup?email={email}")
    assert signup_response.status_code == 200
    assert signup_response.json() == {"message": f"Signed up {email} for Basketball Team"}
    assert email in activities["Basketball Team"]["participants"]

    duplicate_response = client.post(f"/activities/Basketball Team/signup?email={email}")
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_full_activity():
    reset_activities()
    activities["Chess Club"]["max_participants"] = 2

    response = client.post("/activities/Chess Club/signup?email=student@mergington.edu")

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_removes_student():
    reset_activities()
    email = "michael@mergington.edu"

    response = client.delete(f"/activities/Chess Club/participants?email={email}")

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]
