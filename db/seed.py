import json

from psycopg2.extensions import cursor
from psycopg2.extras import execute_values

from api.auth import hash_password
from db.connection import get_cursor

USER_DATA_PATH = "db/data/users.json"
VENUE_DATA_PATH = "db/data/venues.json"
EVENT_DATA_PATH = "db/data/events.json"
RSVP_DATA_PATH = "db/data/rsvps.json"


def drop_users_table(cur: cursor):
    cur.execute("DROP TABLE IF EXISTS rsvps;")


def drop_venues_table(cur: cursor):
    cur.execute("DROP TABLE IF EXISTS events;")


def drop_events_table(cur: cursor):
    cur.execute("DROP TABLE IF EXISTS venues;")


def drop_rsvps_table(cur: cursor):
    cur.execute("DROP TABLE IF EXISTS users;")


def drop_tables(cur: cursor):
    drop_users_table(cur)
    drop_venues_table(cur)
    drop_events_table(cur)
    drop_rsvps_table(cur)


def create_users_table(cur: cursor):
    cur.execute("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """)


def create_venues_table(cur: cursor):
    cur.execute("""
        CREATE TABLE venues (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            address TEXT,
            capacity INTEGER
        );
        """)


def create_events_table(cur: cursor):
    cur.execute("""
        CREATE TABLE events (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description VARCHAR(255),
            starts_at TIMESTAMPTZ NOT NULL,
            ends_at TIMESTAMPTZ NOT NULL,
            organiser_id INTEGER REFERENCES users(id),
            venue_id INTEGER REFERENCES venues(id),
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """)


def create_rsvps_table(cur: cursor):
    cur.execute("""
        CREATE TABLE rsvps (
            id SERIAL PRIMARY KEY,
            attendee_id INTEGER REFERENCES users(id),
            event_id INTEGER REFERENCES events(id),
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """)


def create_tables(cur: cursor):
    create_users_table(cur)
    create_venues_table(cur)
    create_events_table(cur)
    create_rsvps_table(cur)


def insert_user_data(cur: cursor):
    with open(USER_DATA_PATH, "r") as f:
        user_data = json.load(f)
    user_records = [
        (row["email"], hash_password(row["password"]), row["name"]) for row in user_data
    ]

    execute_values(
        cur, "INSERT INTO users (email, password, name) VALUES %s", user_records
    )


def insert_venue_data(cur: cursor):
    with open(VENUE_DATA_PATH, "r") as f:
        venue_data = json.load(f)

    venue_records = [
        (row["name"], row["address"], row["capacity"]) for row in venue_data
    ]

    execute_values(
        cur, "INSERT INTO venues (name, address, capacity) VALUES %s", venue_records
    )


def insert_event_data(cur: cursor):
    with open(EVENT_DATA_PATH, "r") as f:
        event_data = json.load(f)

    event_records = [
        (
            row["title"],
            row["description"],
            row["starts_at"],
            row["ends_at"],
            row["organiser_id"],
            row["venue_id"],
        )
        for row in event_data
    ]

    execute_values(
        cur,
        """
        INSERT INTO events (
            title, description, starts_at,
            ends_at, organiser_id, venue_id
        ) VALUES %s
        """,
        event_records,
    )


def insert_rsvp_data(cur: cursor):
    with open(RSVP_DATA_PATH, "r") as f:
        rsvp_data = json.load(f)

    rsvp_records = [(row["attendee_id"], row["event_id"]) for row in rsvp_data]

    execute_values(
        cur, "INSERT INTO rsvps (attendee_id, event_id) VALUES %s", rsvp_records
    )


def insert_data(cur: cursor):
    insert_user_data(cur)
    insert_venue_data(cur)
    insert_event_data(cur)
    insert_rsvp_data(cur)


def seed():
    """Reset the database to its initial state."""
    with get_cursor() as cur:
        drop_tables(cur)
        create_tables(cur)
        insert_data(cur)


if __name__ == "__main__":
    seed()
