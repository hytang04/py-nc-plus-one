import os
import sys

import pytest

from db.connection import get_connection
from fastapi.testclient import TestClient
from main import app

# Add parent directory of current directory to start of module search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_event():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO events (title, description, starts_at, ends_at, organiser_id, venue_id)
        VALUES (
            'Testing Tech',
            'Some description here',
            '2027-10-04T18:30:00+00:00',
            '2027-10-04T21:30:00+00:00',
            3, 1
        )
        RETURNING id
        """
    )

    event_id = cursor.fetchone()[0]
    conn.commit()
    yield event_id

    cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
    conn.commit()

    cursor.close()
    conn.close()
