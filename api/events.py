from datetime import UTC

from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_user_id
from api.models import (
    RSVP,
    EventGetListResponse,
    EventGetSingleResponse,
    EventPatchRequest,
    EventPostPatchResponse,
    EventPostRequest,
)
from db.connection import get_connection

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", status_code=200, response_model=dict[str, list[EventGetListResponse]])
def list_all_events() -> dict[str, list[EventGetListResponse]]:
    """
    Return all events, ordered by event ID.

    Returns: Dictionary with single key `events` and value a list of `EventList` objects.

    Expected response:
    ```
    {
        "events": [
            {
                "id": 1,
                "title": "Leeds Tech Meetup – June Edition",
                "starts_at": "2026-06-18T18:30:00+01:00",
                "ends_at": "2026-06-18T21:00:00+01:00",
                "location": "Nexus, Leeds, LS2 8PD"
            },
        // ...
        ]
    }
    ```
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
            EventGetListResponse(
                id=r[0],
                title=r[1],
                starts_at=r[2].isoformat(),
                ends_at=r[3].isoformat(),
                location=r[4],
            )
            for r in rows
        ]
    }


@router.get(
    "/{event_id}", status_code=200, response_model=dict[str, EventGetSingleResponse]
)
def get_event_by_id(event_id: int) -> dict[str, EventGetSingleResponse]:
    """
    Return a single event by its event ID.

    Args: `event_id` (integer).

    Returns: Dictionary with single key `event` and value an `EventSingle` object.

    Example response:
    ```
    {
        "event": {
            "id": 2,
            "title": "Intro to Machine Learning Workshop",
            "description": "Hands-on workshop covering perceptrons, neural networks, and classifiers using NumPy and PyTorch.",
            "starts_at": "2026-06-25T10:00:00+01:00",
            "ends_at": "2026-06-25T13:00:00+01:00",
            "location": "Online – Zoom",
            "address": null,
            "capacity": 100,
            "created_at": "2026-06-09T10:38:20.737764+01:00"
        }
    }
    ```
    """
    if event_id < 1:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "BAD_REQUEST",
                "message": f"{event_id} is not a valid integer",
            },
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
        (event_id,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is None:
        raise HTTPException(
            status_code=404, detail={"code": "NOT_FOUND", "message": "Event not found"}
        )

    return {
        "event": EventGetSingleResponse(
            id=row[0],
            title=row[1],
            description=row[2],
            starts_at=row[3].isoformat(),
            ends_at=row[4].isoformat(),
            location=row[5],
            address=row[6],
            capacity=row[7],
            created_at=row[8].isoformat(),
        )
    }


@router.post("/{event_id}/rsvp", status_code=201, response_model=dict[str, RSVP])
def rsvp_event(
    event_id: int, user_id: int = Depends(get_current_user_id)
) -> dict[str, RSVP]:
    """
    RSVP an authenticated user to an event.

    Args: `event_id` (integer).

    Returns: Dictionary with single key `rsvp` and value an `RSVP` object.

    Example response:
    ```
    {
        "rsvp": {
            "id": 55,
            "attendee_id": 1,
            "event_id": 12,
            "created_at": "2025-06-01T11:00:00Z"
        }
    }
    ```
    """
    conn = get_connection()
    cur = conn.cursor()

    # Check that event exists
    cur.execute("SELECT id FROM events WHERE id = %s", (event_id,))
    event = cur.fetchone()
    if event is None:
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=404, detail={"code": "NOT_FOUND", "message": "Event not found"}
        )

    # Check if user has already RSVPed event
    cur.execute(
        """
        SELECT 1 FROM rsvps
        WHERE attendee_id = %s AND event_id = %s
        LIMIT 1
        """,
        (user_id, event_id),
    )
    already_rsvped = cur.fetchone() is not None
    if already_rsvped:
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=409,
            detail={
                "code": "CONFLICT",
                "message": "User has already RSVPed to this event",
            },
        )

    cur.execute(
        """
        INSERT INTO rsvps (attendee_id, event_id)
        VALUES (%s, %s)
        RETURNING id, attendee_id, event_id, created_at
        """,
        (user_id, event_id),
    )
    row = cur.fetchone()
    if row is None:
        conn.rollback()
        cur.close()
        conn.close()
        raise RuntimeError("RSVP insert returned no row")

    conn.commit()
    cur.close()
    conn.close()

    return {
        "rsvp": RSVP(
            id=row[0],
            attendee_id=row[1],
            event_id=row[2],
            created_at=row[3].isoformat(),
        )
    }


@router.delete("/{event_id}/rsvp/me", status_code=204)
def cancel_own_rsvp(event_id: int, user_id: int = Depends(get_current_user_id)) -> None:
    """
    Cancel an authenticated user's own RSVP if it exists.

    Args: `event_id` (integer).
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM rsvps
        WHERE attendee_id = %s AND event_id = %s
        RETURNING id
        """,
        (user_id, event_id),
    )
    deleted_rsvp = cur.fetchone()
    if deleted_rsvp is None:
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": "No RSVP exists for this user on this event",
            },
        )

    conn.commit()
    cur.close()
    conn.close()


@router.post("", status_code=201, response_model=dict[str, EventPostPatchResponse])
def create_event(
    request: EventPostRequest, user_id: int = Depends(get_current_user_id)
) -> dict[str, EventPostPatchResponse]:
    """
    Create a new event, as long as the user is authenticated.

    Returns: Dictionary with single key `event` and value an `EventPostPatchResponse` object.

    Example request:
    ```
    {
        "title": "Summer Rooftop Social",
        "description": "An evening of networking and good vibes.",
        "starts_at": "2025-08-15T18:00:00Z",
        "ends_at": "2025-08-15T21:00:00Z",
        "venue_id": 2
    }
    ```

    Example response:
    ```
    {
        "event": {
            "id": 12,
            "title": "Summer Rooftop Social",
            "description": "An evening of networking and good vibes.",
            "starts_at": "2025-08-15T18:00:00Z",
            "ends_at": "2025-08-15T21:00:00Z",
            "venue_id": 2,
            "organiser_id": 1,
            "created_at": "2025-06-01T10:00:00Z"
        }
    }
    ```
    """
    title, description, starts_at, ends_at, venue_id = (
        request.title,
        request.description,
        request.starts_at,
        request.ends_at,
        request.venue_id,
    )

    # Don't need to check description as it can be empty
    if not title.strip():
        raise HTTPException(
            status_code=400,
            detail={"code": "BAD_REQUEST", "message": "Title is required"},
        )

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO events (
            title, description, starts_at,
            ends_at, organiser_id, venue_id
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING
            id, title, description, starts_at, ends_at,
            venue_id, organiser_id, created_at
        """,
        (title, description, starts_at, ends_at, user_id, venue_id),
    )
    row = cur.fetchone()
    if row is None:
        conn.rollback()
        cur.close()
        conn.close()
        raise RuntimeError("Event insert returned no row")

    conn.commit()
    cur.close()
    conn.close()

    return {
        "event": EventPostPatchResponse(
            id=row[0],
            title=row[1],
            description=row[2],
            starts_at=row[3].isoformat(),
            ends_at=row[4].isoformat(),
            venue_id=row[5],
            organiser_id=row[6],
            created_at=row[7].isoformat(),
        )
    }


@router.patch(
    "/{event_id}", status_code=200, response_model=dict[str, EventPostPatchResponse]
)
def update_event(
    request: EventPatchRequest,
    event_id: int,
    user_id: int = Depends(get_current_user_id),
) -> dict[str, EventPostPatchResponse]:
    """
    Update an event's details, as long as the authenticated user is the organiser.

    Args: `event_id` (integer).

    Returns: Dictionary with single key `event` and value an `EventPostPatchResponse` object.

    Example request:
    ```
    {
        "description": "Updated description, now with live music!",
        "starts_at": "2025-08-16T19:00:00Z",
        "ends_at": "2025-08-16T23:00:00Z"
    }
    ```
    All fields are optional.

    Example response:
    ```
    {
        "event": {
            "id": 12,
            "title": "Summer Rooftop Social",
            "description": "Updated description, now with live music!",
            "starts_at": "2025-08-16T19:00:00Z",
            "ends_at": "2025-08-16T23:00:00Z",
            "venue_id": 3,
            "organiser_id": 1,
            "created_at": "2025-06-01T10:00:00Z"
        }
    }
    ```
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            id, title, description, starts_at, ends_at,
            venue_id, organiser_id, created_at
        FROM events
        WHERE id = %s
        FOR UPDATE
        """,
        (event_id,),
    )
    row = cur.fetchone()
    if row is None:
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=404, detail={"code": "NOT_FOUND", "message": "Event not found"}
        )

    if row[6] != user_id:
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "Only the event organiser may update this event",
            },
        )

    updates = {
        field: getattr(request, field)
        for field in ("description", "starts_at", "ends_at")
        if field in request.model_fields_set
    }

    starts_at = updates.get("starts_at", row[3])
    ends_at = updates.get("ends_at", row[4])
    if starts_at.tzinfo is None:
        starts_at = starts_at.replace(tzinfo=UTC)
    if ends_at.tzinfo is None:
        ends_at = ends_at.replace(tzinfo=UTC)
    if starts_at >= ends_at:
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=400,
            detail={
                "code": "BAD_REQUEST",
                "message": "End time must be after start time",
            },
        )

    if updates:
        assignments = ", ".join(f"{field} = %s" for field in updates)
        cur.execute(
            f"""
            UPDATE events
            SET {assignments}
            WHERE id = %s AND organiser_id = %s
            RETURNING
                id, title, description, starts_at, ends_at,
                venue_id, organiser_id, created_at
            """,
            (*updates.values(), event_id, user_id),
        )
        updated_row = cur.fetchone()
        if updated_row is None:
            conn.rollback()
            cur.close()
            conn.close()
            raise RuntimeError("Event update returned no row")
        row = updated_row

    conn.commit()
    cur.close()
    conn.close()

    return {
        "event": EventPostPatchResponse(
            id=row[0],
            title=row[1],
            description=row[2],
            starts_at=row[3].isoformat(),
            ends_at=row[4].isoformat(),
            venue_id=row[5],
            organiser_id=row[6],
            created_at=row[7].isoformat(),
        )
    }
