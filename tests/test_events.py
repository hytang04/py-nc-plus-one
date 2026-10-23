import pytest

from datetime import datetime
from typing import Optional

from api.auth import create_access_token
from db.connection import get_connection


@pytest.fixture
def event_creation_payload():
    payload = {
        "title": f"Test Event",
        "description": "Created during an integration test",
        "starts_at": "2027-10-04T18:30:00Z",
        "ends_at": "2027-10-04T21:30:00Z",
        "venue_id": 1,
    }
    yield payload

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE title = %s", (payload["title"],))
    conn.commit()
    cur.close()
    conn.close()


def test_list_all_events_returns_correct_shape(client, sample_event):
    response = client.get("/api/events")

    assert response.status_code == 200
    event_data = response.json()

    assert isinstance(event_data, dict)
    assert "events" in event_data.keys()
    assert [event["id"] for event in event_data
                 ["events"]] == list(range(1, 11)) + [sample_event]


def test_list_all_events_returns_correct_schema(client):
    response = client.get("/api/events")
    data = response.json()

    expected_keys = {"id", "title", "starts_at", "ends_at", "location"}

    for event in data["events"]:
        assert expected_keys == event.keys()
        assert isinstance(event["id"], int)
        assert isinstance(event["title"], str)
        assert isinstance(event["starts_at"], str)
        assert isinstance(event["ends_at"], str)
        assert isinstance(event["location"], str)


def test_get_event_by_id_returns_correct_event(client, sample_event):
    response = client.get(f"/api/events/{sample_event}")

    assert response.status_code == 200
    event_data = response.json()
    assert event_data["event"]["id"] == sample_event


def test_get_event_by_id_returns_correct_shape(client, sample_event):
    response = client.get(f"/api/events/{sample_event}")

    assert response.status_code == 200
    event_data = response.json()
    assert isinstance(event_data, dict)
    assert "event" in event_data.keys()
    assert isinstance(event_data["event"], dict)


def test_get_event_by_id_returns_correct_schema(client):
    response = client.get("/api/events/1")
    event_data = response.json()

    expected_keys = {"id", "title", "description", "starts_at",
                     "ends_at", "location", "address", "capacity", "created_at"}

    event = event_data["event"]
    assert expected_keys == event.keys()
    assert isinstance(event["id"], int)
    assert isinstance(event["title"], str)
    assert isinstance(event["description"], Optional[str])
    assert isinstance(event["starts_at"], str)
    assert isinstance(event["ends_at"], str)
    assert isinstance(event["location"], str)
    assert isinstance(event["address"], Optional[str])
    assert isinstance(event["capacity"], int)
    assert isinstance(event["created_at"], str)


def test_get_event_by_id_not_found_returns_404(client):
    response = client.get("/api/events/99999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_get_event_by_id_invalid_integer_returns_400(client):
    response = client.get("/api/events/-4")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"


def test_rsvp_event_returns_created_rsvp(client, sample_event):
    token = create_access_token(1)

    response = client.post(
        f"/api/events/{sample_event}/rsvp",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    rsvp = response.json()["rsvp"]
    assert set(rsvp) == {"id", "attendee_id", "event_id", "created_at"}
    assert rsvp["attendee_id"] == 1
    assert rsvp["event_id"] == sample_event
    assert isinstance(rsvp["created_at"], str)


@pytest.mark.parametrize(
    "headers",
    [None, {"Authorization": "Bearer invalid-token"}],
    ids=["missing-token", "invalid-token"],
)
def test_rsvp_user_to_event_without_valid_token_returns_401(client, sample_event, headers):
    response = client.post(
        f"/api/events/{sample_event}/rsvp",
        headers=headers,
    )

    assert response.status_code == 401


def test_rsvp_event_nonexistent_event_returns_404(client):
    token = create_access_token(1)

    response = client.post(
        "/api/events/99999/rsvp",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_rsvp_event_twice_returns_409_on_duplicate(client, sample_event):
    token = create_access_token(1)
    headers = {"Authorization": f"Bearer {token}"}
    url = f"/api/events/{sample_event}/rsvp"

    first_response = client.post(url, headers=headers)
    duplicate_response = client.post(url, headers=headers)

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["error"]["code"] == "CONFLICT"


def test_cancel_own_rsvp_returns_204(client, sample_event):
    token = create_access_token(1)
    headers = {"Authorization": f"Bearer {token}"}
    rsvp_response = client.post(
        f"/api/events/{sample_event}/rsvp",
        headers=headers,
    )
    assert rsvp_response.status_code == 201

    response = client.delete(
        f"/api/events/{sample_event}/rsvp/me",
        headers=headers,
    )

    assert response.status_code == 204
    assert response.content == b""

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT EXISTS (SELECT 1 FROM rsvps WHERE attendee_id = %s AND event_id = %s)",
        (1, sample_event),
    )
    assert cur.fetchone()[0] is False
    cur.close()
    conn.close()


def test_cancel_rsvp_for_another_user_does_not_delete_their_rsvp(
    client, sample_event
):
    owner_token = create_access_token(2)
    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    rsvp_response = client.post(
        f"/api/events/{sample_event}/rsvp",
        headers=owner_headers,
    )
    assert rsvp_response.status_code == 201

    response = client.delete(
        f"/api/events/{sample_event}/rsvp/me",
        headers={"Authorization": f"Bearer {create_access_token(1)}"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT EXISTS (SELECT 1 FROM rsvps WHERE attendee_id = %s AND event_id = %s)",
        (2, sample_event),
    )
    assert cur.fetchone()[0] is True
    cur.close()
    conn.close()


def test_cancel_missing_rsvp_returns_404(client, sample_event):
    response = client.delete(
        f"/api/events/{sample_event}/rsvp/me",
        headers={"Authorization": f"Bearer {create_access_token(1)}"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.parametrize(
    "headers",
    [None, {"Authorization": "Bearer invalid-token"}],
    ids=["missing-token", "invalid-token"],
)
def test_cancel_rsvp_without_valid_token_returns_401(
    client, sample_event, headers
):
    response = client.delete(
        f"/api/events/{sample_event}/rsvp/me",
        headers=headers,
    )

    assert response.status_code == 401


def test_create_event_returns_created_event_and_uses_organiser_token(
    client, event_creation_payload
):
    token = create_access_token(2)
    response = client.post(
        "/api/events",
        json=event_creation_payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    event = response.json()["event"]
    assert set(event) == {
        "id", "title", "description", "starts_at", "ends_at",
        "venue_id", "organiser_id", "created_at",
    }
    assert event["title"] == event_creation_payload["title"]
    assert event["organiser_id"] == 2
    assert event["venue_id"] == event_creation_payload["venue_id"]
    assert datetime.fromisoformat(event["starts_at"]) == datetime.fromisoformat(
        "2027-10-04T18:30:00+00:00"
    )
    assert datetime.fromisoformat(event["ends_at"]) == datetime.fromisoformat(
        "2027-10-04T21:30:00+00:00"
    )


def test_create_event_rejects_organiser_id_in_request(
    client, event_creation_payload
):
    # Set union event payload with organiser_id
    payload = event_creation_payload | {"organiser_id": 1}
    response = client.post(
        "/api/events",
        json=payload,
        headers={"Authorization": f"Bearer {create_access_token(2)}"},
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    "headers",
    [None, {"Authorization": "Bearer invalid-token"}],
    ids=["missing-token", "invalid-token"],
)
def test_create_event_without_valid_token_returns_401(
    client, event_creation_payload, headers
):
    response = client.post(
        "/api/events",
        json=event_creation_payload,
        headers=headers,
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "missing_field",
    ["title", "starts_at", "ends_at", "venue_id"],
)
def test_create_event_missing_required_field_returns_400(
    client, event_creation_payload, missing_field
):
    payload = event_creation_payload.copy()
    payload.pop(missing_field)

    response = client.post(
        "/api/events",
        json=payload,
        headers={"Authorization": f"Bearer {create_access_token(1)}"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"


@pytest.mark.parametrize("date_field", ["starts_at", "ends_at"])
def test_create_event_invalid_date_returns_400(
    client, event_creation_payload, date_field
):
    payload = event_creation_payload.copy()
    payload[date_field] = "not-an-iso-date"

    response = client.post(
        "/api/events",
        json=payload,
        headers={"Authorization": f"Bearer {create_access_token(1)}"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"


def test_create_event_start_after_end_returns_400(
    client, event_creation_payload
):
    payload = event_creation_payload.copy()
    payload["starts_at"] = "2027-10-04T21:30:00Z"
    payload["ends_at"] = "2027-10-04T18:30:00Z"

    response = client.post(
        "/api/events",
        json=payload,
        headers={"Authorization": f"Bearer {create_access_token(1)}"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"


def test_create_event_equal_start_and_end_is_valid(
    client, event_creation_payload
):
    payload = event_creation_payload.copy()
    payload["ends_at"] = payload["starts_at"]

    response = client.post(
        "/api/events",
        json=payload,
        headers={"Authorization": f"Bearer {create_access_token(1)}"},
    )

    assert response.status_code == 201


def test_create_event_empty_title_returns_400(client, event_creation_payload):
    payload = event_creation_payload.copy()
    payload["title"] = " "

    response = client.post(
        "/api/events",
        json=payload,
        headers={"Authorization": f"Bearer {create_access_token(1)}"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"
