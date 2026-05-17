"""Database schema helpers."""

from __future__ import annotations

from pathlib import Path

import psycopg

_SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def ensure_schema(conninfo: str) -> None:
    """Create application tables if they do not exist."""
    schema_sql = _SCHEMA_PATH.read_text(encoding="utf-8")
    with psycopg.connect(conninfo) as conn:
        conn.execute(schema_sql)
        conn.commit()
