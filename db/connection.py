import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parent.parent / ".env")

required_settings = ("PGDATABASE", "PGUSER", "PGPASSWORD", "PGHOST")
missing_settings = [
    setting for setting in required_settings if not os.getenv(setting)]

if missing_settings:
    raise RuntimeError(
        "Missing database settings in .env: " + ", ".join(missing_settings)
    )

connection = psycopg2.connect(
    dbname=os.environ["PGDATABASE"],
    user=os.environ["PGUSER"],
    password=os.environ["PGPASSWORD"],
    host=os.environ["PGHOST"],
    port=os.environ["PGPORT"]
)
