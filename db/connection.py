import os
import psycopg2

from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

required_settings = ("PGDATABASE", "PGUSER", "PGPASSWORD", "PGHOST", "PGPORT")
missing_settings = [
    setting for setting in required_settings if not os.getenv(setting)]

if missing_settings:
    raise RuntimeError(
        "Missing database settings in .env: " + ", ".join(missing_settings)
    )


def get_connection():
    return psycopg2.connect(
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        host=os.environ["PGHOST"],
        port=os.environ["PGPORT"]
    )
