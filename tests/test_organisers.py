def test_get_organiser_stats_returns_correct_schema(client):
    response = client.get("/api/organisers/1/stats")
    assert response.status_code == 200
    data = response.json()

    expected_keys = {
        "organiser_id",
        "name",
        "total_events",
        "avg_attendance",
        "best_attended_count",
        "organiser_rank",
    }

    assert "stats" in data
    assert expected_keys == data["stats"].keys()
    assert isinstance(data["stats"]["organiser_id"], int)
    assert isinstance(data["stats"]["name"], str)
    assert isinstance(data["stats"]["total_events"], int)
    assert isinstance(data["stats"]["avg_attendance"], float)
    assert isinstance(data["stats"]["best_attended_count"], int)
    assert isinstance(data["stats"]["organiser_rank"], int)


def test_get_organiser_stats_not_found_returns_404(client):
    response = client.get("/api/organisers/99999/stats")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
