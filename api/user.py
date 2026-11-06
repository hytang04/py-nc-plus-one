from fastapi import APIRouter, Depends

from api.auth import get_current_user_id
from api.models import UserEventGetListResponse
from db.connection import get_connection

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get(
    "/me/events",
    status_code=200,
    response_model=dict[str, list[UserEventGetListResponse]],
)
def list_all_rsvp_events(
    user_id: int = Depends(get_current_user_id),
) -> dict[str, list[UserEventGetListResponse]]:
    """
    Return all events the authenticated user has RSVPed to, ordered by event ID.

    Returns: Dictionary with single key `events` and value a list of `UserEventGetListResponse` objects.

    Expected response:
    ```
    {
        "events": [
            {
                "id": 8,
                "title": "Spring Networking Night",
                "starts_at": "2025-04-10T18:00:00Z",
                "rsvp_date": "2025-03-01T09:00:00Z",
                "event_rank": 1,
                "total_rsvps": 3
            },
            {
                "id": 12,
                "title": "Summer Rooftop Social",
                "starts_at": "2025-08-16T19:00:00Z",
                "rsvp_date": "2025-06-01T11:00:00Z",
                "event_rank": 2,
                "total_rsvps": 3
            }
        ]
    }
    ```
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            e.id, e.title, e.starts_at, r.created_at,
            ROW_NUMBER() OVER (
                PARTITION BY r.attendee_id
                ORDER BY e.starts_at ASC
            ),
            COUNT(*) OVER (
                PARTITION BY r.attendee_id
            )
        FROM rsvps r
        JOIN events e
        ON r.event_id = e.id
        WHERE r.attendee_id = %s
        ORDER BY e.id;
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "events": [
            UserEventGetListResponse(
                id=r[0],
                title=r[1],
                starts_at=r[2].isoformat(),
                rsvp_date=r[3].isoformat(),
                event_rank=r[4],
                total_rsvps=r[5],
            )
            for r in rows
        ]
    }
