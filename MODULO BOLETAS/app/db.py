import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


def _db_ssl_mode() -> str:
    return "require" if os.getenv("DB_SSL", "false").lower() == "true" else "disable"


def get_conn() -> psycopg.Connection:
    conninfo = (
        f"host={os.getenv('DB_HOST', 'localhost')} "
        f"port={os.getenv('DB_PORT', '5432')} "
        f"dbname={os.getenv('DB_NAME', 'boletas_db')} "
        f"user={os.getenv('DB_USER', 'boletas_user')} "
        f"password={os.getenv('DB_PASSWORD', 'boletas_pass')} "
        f"sslmode={_db_ssl_mode()}"
    )
    return psycopg.connect(conninfo=conninfo, row_factory=dict_row)


def run_schema() -> None:
    schema_path = Path(os.getenv("DB_SCHEMA_PATH", "app/schema.sql"))
    sql = schema_path.read_text(encoding="utf-8")
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()

