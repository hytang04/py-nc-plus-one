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


class EventSingle(BaseModel):
    id: int
    title: str
    description: Optional[str]
    starts_at: str
    ends_at: str
    location: str
    address: Optional[str]
    capacity: int
    created_at: str


@router.get("", status_code=200, response_model=dict[str, list[EventList]])
def list_all_events() -> dict[str, list[EventList]]:
    """
    Return all events, ordered by event ID.

    The response body is a dictionary with a single key `events` and its value a list of `EventList` objects.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT e.id, e.title, e.starts_at, e.ends_at, v.name
        FROM events e
        LEFT JOIN venues v
        ON e.venue_id = v.id
        ORDER BY e.id;
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


@router.get("/{event_id}", status_code=200, response_model=dict[str, EventSingle])
def get_event_by_id(event_id: int) -> dict[str, EventSingle]:
    """
    Return a single event by its event ID.

    The response body is a dictionary with a single key `event` and its value an `EventSingle` object.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT e.id, e.title, e.description, e.starts_at, e.ends_at,
            v.name, v.address, v.capacity, e.created_at
        FROM events e
        LEFT JOIN venues v
        ON e.venue_id = v.id
        WHERE e.id = %s;
        """,
        (event_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "Event not found"}
        )

    return {
        "event": {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "starts_at": row[3].isoformat(),
            "ends_at": row[4].isoformat(),
            "location": row[5],
            "address": row[6],
            "capacity": row[7],
            "created_at": row[8].isoformat()
        }
    }
