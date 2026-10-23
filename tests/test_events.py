import pytest

from db.connection import get_connection
from typing import Optional


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
