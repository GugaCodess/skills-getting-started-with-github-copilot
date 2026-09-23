import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(
        {
            "Chess Club": {
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12,
                "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
            },
            "Programming Class": {
                "description": "Learn programming fundamentals and build software projects",
                "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                "max_participants": 20,
                "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
            },
            "Gym Class": {
                "description": "Physical education and sports activities",
                "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                "max_participants": 30,
                "participants": ["john@mergington.edu", "olivia@mergington.edu"],
            },
            "Soccer Club": {
                "description": "Practice soccer skills and compete in friendly matches",
                "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
                "max_participants": 24,
                "participants": [],
            },
            "Track and Field": {
                "description": "Train for running, jumping, and throwing events",
                "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 30,
                "participants": [],
            },
            "Art Club": {
                "description": "Explore drawing, painting, and other visual art techniques",
                "schedule": "Mondays, 3:30 PM - 5:00 PM",
                "max_participants": 20,
                "participants": [],
            },
            "Drama Club": {
                "description": "Develop acting skills and perform plays for the school community",
                "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
                "max_participants": 25,
                "participants": [],
            },
            "Debate Club": {
                "description": "Build public speaking and critical thinking skills through debate",
                "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
                "max_participants": 18,
                "participants": [],
            },
            "Science Club": {
                "description": "Conduct experiments and explore fascinating scientific ideas",
                "schedule": "Thursdays, 3:30 PM - 4:30 PM",
                "max_participants": 20,
                "participants": [],
            },
        }
    )
    yield
    activities.clear()


client = TestClient(app)


def test_get_activities_returns_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "participants" in response.json()["Chess Club"]


def test_signup_for_activity_success():
    email = "new.student@mergington.edu"

    response = client.post(
        "/activities/Soccer Club/signup?email=new.student@mergington.edu"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Soccer Club"
    assert email in activities["Soccer Club"]["participants"]


def test_signup_rejects_duplicate_registration():
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_full_activity():
    activities["Chess Club"]["participants"] = [
        f"student{i}@mergington.edu" for i in range(12)
    ]

    response = client.post("/activities/Chess Club/signup?email=overflow@mergington.edu")

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Chess Club"
    email = "student.remove@mergington.edu"

    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    assert signup_response.status_code == 200

    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_not_found():
    response = client.delete(
        "/activities/Chess Club/unregister?email=missing@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
