from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional


from db.connection import get_connection


router = APIRouter(prefix="/events", tags=["events"])


class EventList(BaseModel):
    id: int
    title: str
    starts_at: str
    ends_at: str
    location: str


@router.get("", status_code=200, response_model=dict[str, list[EventList]])
def list_events() -> dict[str, list[EventList]]:
    """
    Return all events, ordered by event ID.

    The response body is a dictionary with a single key `events` and its value a list of `Event`s.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT e.id, e.title, e.starts_at, e.ends_at, v.name
        FROM events e
        LEFT JOIN venues v
        ON e.venue_id = v.id;
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "events": [
            {
                "id": r[0],
                "title": r[1],
                "starts_at": r[2].isoformat(),
                "ends_at": r[3].isoformat(),
                "location": r[4]
            } for r in rows
        ]
    }
