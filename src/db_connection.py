"""Reusable SQLAlchemy connection helpers for the local MySQL database."""
from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from dotenv import load_dotenv
from sqlalchemy import Engine, URL, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def get_engine() -> Engine:
    """Create an engine from environment variables without embedding credentials."""
    required = ("MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_HOST", "MYSQL_DATABASE")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            "Missing database settings: " + ", ".join(missing) + ". Copy .env.example to .env."
        )
    url = URL.create(
        "mysql+mysqlconnector",
        username=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        host=os.environ["MYSQL_HOST"],
        port=int(os.getenv("MYSQL_PORT", "3306")),
        database=os.environ["MYSQL_DATABASE"],
    )
    return create_engine(url, pool_pre_ping=True, future=True)


@contextmanager
def get_connection() -> Iterator[object]:
    """Yield a managed connection and translate common connection failures."""
    engine = get_engine()
    try:
        with engine.begin() as connection:
            yield connection
    except SQLAlchemyError as exc:
        raise RuntimeError(
            "Could not connect to MySQL. Confirm that MySQL is running and .env is correct."
        ) from exc
    finally:
        engine.dispose()


def test_connection() -> None:
    with get_connection() as connection:
        connection.execute(text("SELECT 1"))
    print("MySQL connection succeeded.")


if __name__ == "__main__":
    test_connection()
