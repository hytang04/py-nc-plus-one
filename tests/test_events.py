import pytest

from db.connection import get_connection


def test_list_events_returns_correctly(client, sample_event):
    response = client.get("/events")
    assert response.status_code == 200

    assert "events" in response.json().keys()

    assert [event["id"] for event in response.json()
                 ["events"]] == list(range(1, 12))
