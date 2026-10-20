from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional


from db.connection import get_connection


router = APIRouter(prefix="/events", tags=["events"])


class Event(BaseModel):
    id: int
    title: str
    starts_at: str
    ends_at: str
    location: Optional[str]


@router.get("", status_code=200, response_model=dict[str, list[Event]])
def list_events():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT e.id, e.title, e.starts_at, e.ends_at, v.address
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
