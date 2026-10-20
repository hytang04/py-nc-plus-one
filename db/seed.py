import json

from connection import conn
from psycopg2.extensions import connection, cursor
from psycopg2.extras import execute_values

USER_DATA_PATH = "db/data/users.json"


def drop_tables(conn: connection, cursor: cursor):
    cursor.execute("DROP TABLE IF EXISTS users;")
    conn.commit()


def create_tables(conn: connection, cursor: cursor):
    cursor.execute(
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


def insert_data(conn: connection, cursor: cursor):
    with open(USER_DATA_PATH, "r") as f:
        users_data = json.load(f)

    user_records = [
        (row["name"], row["email"], row["password"]) for row in users_data
    ]

    execute_values(
        cursor,
        "INSERT INTO users (email, password, name) VALUES %s",
        user_records
    )
    conn.commit()


def seed(conn: connection):
    """Reset the database to its initial state."""
    cursor = conn.cursor()

    drop_tables(conn, cursor)
    create_tables(conn, cursor)
    insert_data(conn, cursor)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    seed(conn)
