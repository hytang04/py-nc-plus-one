import os
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv
from psycopg2 import pool

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

PGUSER = os.environ.get("PGUSER")
PGPASSWORD = os.environ.get("PGPASSWORD")
PGHOST = os.environ.get("PGHOST")
PGPORT = os.environ.get("PGPORT", "5432")
PGDATABASE = os.environ.get("PGDATABASE")

# Validate presence of critical connection variables
required_vars = {
    "PGUSER": PGUSER,
    "PGPASSWORD": PGPASSWORD,
    "PGHOST": PGHOST,
    "PGDATABASE": PGDATABASE,
}
missing = [k for k, v in required_vars.items() if not v]
if missing:
    raise NameError(f"Missing required environment variables: {', '.join(missing)}")

db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    user=PGUSER,
    password=PGPASSWORD,
    host=PGHOST,
    port=PGPORT,
    database=PGDATABASE,
)


@contextmanager
def get_cursor():
    conn = db_pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            yield cur
    finally:
        db_pool.putconn(conn)
