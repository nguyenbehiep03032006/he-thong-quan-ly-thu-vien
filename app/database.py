import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()


def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "library_db"),
        user=os.getenv("POSTGRES_USER", "library_user"),
        password=os.getenv("POSTGRES_PASSWORD"),
        row_factory=dict_row,
    )
