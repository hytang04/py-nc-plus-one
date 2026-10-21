import pytest

from db.connection import get_connection
from typing import Optional


def test_list_events_returns_correct_shape(client, sample_event):
    response = client.get("/events")

    assert response.status_code == 200
    event_data = response.json()

    assert isinstance(event_data, dict)
    assert "events" in event_data.keys()
    assert [event["id"] for event in event_data
                 ["events"]] == list(range(1, 11)) + [sample_event]


def test_list_events_returns_correct_schema(client):
    response = client.get("/events")
    data = response.json()

    expected_keys = {"id", "title", "starts_at", "ends_at", "location"}

    for event in data["events"]:
        assert expected_keys == event.keys()
        assert isinstance(event["id"], int)
        assert isinstance(event["title"], str)
        assert isinstance(event["starts_at"], str)
        assert isinstance(event["ends_at"], str)
        assert isinstance(event["location"], Optional[str])
