from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_user_id
from api.models import EventList, EventSingle, RSVP
from db.connection import get_connection


router = APIRouter(prefix="/api/events", tags=["events"])


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
    if event_id < 1:
        raise HTTPException(
            status_code=400,
            detail={"code": "BAD_REQUEST",
                    "message": f"{event_id} is not a valid integer"}
        )
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


@router.post("/{event_id}/rsvp", status_code=201, response_model=dict[str, RSVP])
def rsvp_user_to_event(
    event_id: int, user_id: int = Depends(get_current_user_id)
) -> dict[str, RSVP]:
    conn = get_connection()
    cur = conn.cursor()

    # Check that event exists
    cur.execute(
        "SELECT id FROM events WHERE id = %s",
        (event_id,)
    )
    event = cur.fetchone()
    if event is None:
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": "Event not found"
            }
        )

    # Check if user has already RSVPed event
    cur.execute(
        """
        SELECT EXISTS (
            SELECT 1 FROM rsvps
            WHERE attendee_id = %s AND event_id = %s
        )
        """,
        (user_id, event_id)
    )
    already_rsvped = cur.fetchone()[0]
    if already_rsvped:
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=409,
            detail={
                "code": "CONFLICT",
                "message": "User has already RSVPed to this event"
            }
        )

    cur.execute(
        """
        INSERT INTO rsvps (attendee_id, event_id)
        VALUES (%s, %s)
        RETURNING id, attendee_id, event_id, created_at
        """,
        (user_id, event_id)
    )
    row = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return {
        "rsvp": {
            "id": row[0],
            "attendee_id": row[1],
            "event_id": row[2],
            "created_at": row[3].isoformat()
        }
    }


@router.delete("/{event_id}/rsvp/me", status_code=204)
def cancel_own_rsvp(event_id: int, user_id: int = Depends(get_current_user_id)) -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM rsvps
        WHERE attendee_id = %s AND event_id = %s
        RETURNING id
        """,
        (user_id, event_id)
    )
    deleted_rsvp = cur.fetchone()
    if deleted_rsvp is None:
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": "No RSVP exists for this user on this event"
            }
        )

    conn.commit()
    cur.close()
    conn.close()
