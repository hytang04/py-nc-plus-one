import pytest

from api.auth import create_access_token


def test_list_all_rsvp_events_returns_correct_shape(client):
    token = create_access_token(1)

    response = client.get(
        "/api/user/me/events", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    event_data = response.json()

    assert isinstance(event_data, dict)
    assert "events" in event_data
    assert len(event_data["events"]) == 4


def test_list_all_events_returns_correct_schema(client):
    token = create_access_token(1)
    response = client.get(
        "/api/user/me/events", headers={"Authorization": f"Bearer {token}"}
    )
    data = response.json()

    expected_keys = {
        "id",
        "title",
        "starts_at",
        "rsvp_date",
        "event_rank",
        "total_rsvps",
    }

    for event in data["events"]:
        assert expected_keys == event.keys()
        assert isinstance(event["id"], int)
        assert isinstance(event["title"], str)
        assert isinstance(event["starts_at"], str)
        assert isinstance(event["event_rank"], int)
        assert isinstance(event["rsvp_date"], str)
        assert isinstance(event["total_rsvps"], int)


@pytest.mark.parametrize(
    "headers",
    [None, {"Authorization": "Bearer invalid-token"}],
    ids=["missing-token", "invalid-token"],
)
def test_list_all_rsvp_events_without_valid_token_returns_401(client, headers):
    response = client.get(
        "/api/user/me/events",
        headers=headers,
    )

    assert response.status_code == 401
