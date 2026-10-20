import json

from connection import conn
from psycopg2.extensions import connection, cursor
from psycopg2.extras import execute_values

USER_DATA_PATH = "db/data/users.json"
VENUE_DATA_PATH = "db/data/venues.json"
EVENT_DATA_PATH = "db/data/events.json"
RSVP_DATA_PATH = "db/data/rsvps.json"


def drop_users_table(conn: connection, cur: cursor):
    cur.execute("DROP TABLE IF EXISTS rsvps;")
    conn.commit()


def drop_venues_table(conn: connection, cur: cursor):
    cur.execute("DROP TABLE IF EXISTS events;")
    conn.commit()


def drop_events_table(conn: connection, cur: cursor):
    cur.execute("DROP TABLE IF EXISTS venues;")
    conn.commit()


def drop_rsvps_table(conn: connection, cur: cursor):
    cur.execute("DROP TABLE IF EXISTS users;")
    conn.commit()


def drop_tables(conn: connection, cur: cursor):
    drop_users_table(conn, cur)
    drop_venues_table(conn, cur)
    drop_events_table(conn, cur)
    drop_rsvps_table(conn, cur)


def create_users_table(conn: connection, cur: cursor):
    cur.execute(
        """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
    )
    conn.commit()


def create_venues_table(conn: connection, cur: cursor):
    cur.execute(
        """
        CREATE TABLE venues (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            address TEXT,
            capacity INT
        );
        """
    )
    conn.commit()


def create_events_table(conn: connection, cur: cursor):
    cur.execute(
        """
        CREATE TABLE events (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description VARCHAR(255),
            starts_at TIMESTAMPTZ NOT NULL,
            ends_at TIMESTAMPTZ NOT NULL,
            organiser_id INT REFERENCES users(id),
            venue_id INT REFERENCES venues(id),
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
    )
    conn.commit()


def create_rsvps_table(conn: connection, cur: cursor):
    cur.execute(
        """
        CREATE TABLE rsvps (
            id SERIAL PRIMARY KEY,
            attendee_id INT REFERENCES users(id),
            event_id INT REFERENCES events(id),
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
    )
    conn.commit()


def create_tables(conn: connection, cur: cursor):
    create_users_table(conn, cur)
    create_venues_table(conn, cur)
    create_events_table(conn, cur)
    create_rsvps_table(conn, cur)


def insert_user_data(conn: connection, cur: cursor):
    with open(USER_DATA_PATH, "r") as f:
        user_data = json.load(f)

    user_records = [
        (row["name"], row["email"], row["password"]) for row in user_data
    ]

    execute_values(
        cur,
        "INSERT INTO users (email, password, name) VALUES %s",
        user_records
    )
    conn.commit()


def insert_venue_data(conn: connection, cur: cursor):
    with open(VENUE_DATA_PATH, "r") as f:
        venue_data = json.load(f)

    venue_records = [
        (row["name"], row["address"], row["capacity"]) for row in venue_data
    ]

    execute_values(
        cur,
        "INSERT INTO venues (name, address, capacity) VALUES %s",
        venue_records
    )
    conn.commit()


def insert_event_data(conn: connection, cur: cursor):
    with open(EVENT_DATA_PATH, "r") as f:
        event_data = json.load(f)

    event_records = [
        (
            row["title"], row["description"],
            row["starts_at"], row["ends_at"],
            row["organiser_id"], row["venue_id"]
        ) for row in event_data
    ]

    execute_values(
        cur,
        """
        INSERT INTO events (
            title, description, starts_at,
            ends_at, organiser_id, venue_id
        ) VALUES %s
        """,
        event_records
    )
    conn.commit()


def insert_rsvp_data(conn: connection, cur: cursor):
    with open(RSVP_DATA_PATH, "r") as f:
        rsvp_data = json.load(f)

    rsvp_records = [
        (row["attendee_id"], row["event_id"]) for row in rsvp_data
    ]

    execute_values(
        cur,
        "INSERT INTO rsvps (attendee_id, event_id) VALUES %s",
        rsvp_records
    )
    conn.commit()


def insert_data(conn: connection, cur: cursor):
    insert_user_data(conn, cur)
    insert_venue_data(conn, cur)
    insert_event_data(conn, cur)
    insert_rsvp_data(conn, cur)


def seed(conn: connection):
    """Reset the database to its initial state."""
    cur = conn.cursor()

    drop_tables(conn, cur)
    create_tables(conn, cur)
    insert_data(conn, cur)

    cur.close()
    conn.close()


if __name__ == "__main__":
    seed(conn)
