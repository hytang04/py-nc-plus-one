from fastapi import APIRouter

from api.models import OrganiserResponse
from db.connection import get_connection

router = APIRouter(prefix="/api/organisers", tags=["organisers"])


@router.get(
    "/{organiser_id}/stats",
    status_code=200,
    response_model=dict[str, list[OrganiserResponse]],
)
def get_organiser_stats(
    organiser_id: int,
) -> dict[str, list[OrganiserResponse]]:
    """
    Return aggregate statistics for an organiser, including how they rank compared to all other organisers.

    Returns: Dictionary with single key `stats` and value a list of `OrganiserGetResponse` objects.

    Expected response:
    ```
    {
        "stats": {
            "organiser_id": 1,
            "name": "Alice Smith",
            "total_events": 5,
            "avg_attendance": 28.4,
            "best_attended_count": 61,
            "organiser_rank": 2
        }
    }
    ```
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        WITH event_attendance AS (
            -- Compute attendee count per event
            SELECT
                e.id AS event_id,
                e.organiser_id,
                COUNT(r.id) AS attendee_count
            FROM events e
            LEFT JOIN rsvps r ON e.id = r.event_id
            GROUP BY e.id, e.organiser_id
        ),
        organiser_aggregates AS (
            -- Aggregate per organiser and compute ranking across all organisers
            SELECT
                u.id AS organiser_id,
                u.name,
                COUNT(ea.event_id) AS total_events,
                ROUND(AVG(ea.attendee_count), 1) AS avg_attendance,
                COALESCE(MAX(ea.attendee_count), 0) AS best_attended_count,
                DENSE_RANK() OVER (
                    ORDER BY COUNT(ea.event_id) DESC
                ) AS organiser_rank
            FROM users u
            JOIN event_attendance ea ON u.id = ea.organiser_id
            GROUP BY u.id, u.name
            HAVING COUNT(ea.event_id) > 0
        )
        -- Filter for requested organiser
        SELECT
            organiser_id, name, total_events,
            avg_attendance, best_attended_count, organiser_rank
        FROM organiser_aggregates
        WHERE organiser_id = %s
        """,
        (organiser_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "stats": [
            OrganiserResponse(
                organiser_id=r[0],
                name=r[1],
                total_events=r[2],
                avg_attendance=r[3],
                best_attended_count=r[4],
                organiser_rank=r[5],
            )
            for r in rows
        ]
    }
