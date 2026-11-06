import pytest
from fastapi.testclient import TestClient

from db.connection import get_cursor
from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_event():
    """Create a single event and delete it safely during a test's lifespan."""
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO events (title, description, starts_at, ends_at, organiser_id, venue_id)
            VALUES (
                'Testing Tech',
                'Some description here',
                '2027-10-04T18:30:00+00:00',
                '2027-10-04T21:30:00+00:00',
                3,
                1
            )
            RETURNING id
            """)

        row = cur.fetchone()

    if row is None:
        return False

    event_id = row[0]
    yield event_id

    with get_cursor() as cur:
        cur.execute("DELETE FROM rsvps WHERE event_id = %s", (event_id,))
        cur.execute("DELETE FROM events WHERE id = %s", (event_id,))
