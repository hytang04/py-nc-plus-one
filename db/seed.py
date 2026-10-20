import json

from connection import conn
from psycopg2.extensions import connection, cursor
from psycopg2.extras import execute_values

USER_DATA_PATH = "db/data/users.json"
VENUE_DATA_PATH = "db/data/venues.json"


def drop_users_table(conn: connection, cur: cursor):
    cur.execute("DROP TABLE IF EXISTS users;")
    conn.commit()


def drop_venues_table(conn: connection, cur: cursor):
    cur.execute("DROP TABLE IF EXISTS venues;")
    conn.commit()


def drop_tables(conn: connection, cur: cursor):
    drop_users_table(conn, cur)
    drop_venues_table(conn, cur)


def create_user_table(conn: connection, cur: cursor):
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


def create_venue_table(conn: connection, cur: cursor):
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


def create_tables(conn: connection, cur: cursor):
    create_user_table(conn, cur)
    create_venue_table(conn, cur)


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


def insert_data(conn: connection, cur: cursor):
    insert_user_data(conn, cur)
    insert_venue_data(conn, cur)


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
