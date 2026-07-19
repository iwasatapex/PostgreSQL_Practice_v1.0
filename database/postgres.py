"""
database/postgres.py

PostgreSQL database helper.

Handles:
- Connecting
- Disconnecting
- Executing SQL
- Fetching results
- Transaction handling
"""

from __future__ import annotations

from typing import Any

import psycopg2
from psycopg2.extensions import connection, cursor

from config import DATABASE


class PostgreSQL:
    """Simple PostgreSQL helper."""

    def __init__(self) -> None:
        self.connection: connection | None = None
        self.cursor: cursor | None = None

    def connect(self) -> None:
        """Open a database connection."""

        if self.connection is not None:
            return

        self.connection = psycopg2.connect(**DATABASE)
        self.cursor = self.connection.cursor()

        print("✅ Connected to PostgreSQL")

    def disconnect(self) -> None:
        """Close the database connection."""

        if self.cursor is not None:
            self.cursor.close()

        if self.connection is not None:
            self.connection.close()

        self.connection = None
        self.cursor = None

        print("🔒 Database connection closed")

    def execute(self, query: str, params: tuple[Any, ...] | None = None) -> None:
        """Execute INSERT, UPDATE, DELETE or DDL statements."""

        if self.cursor is None:
            raise RuntimeError("Database is not connected.")

        self.cursor.execute(query, params)

        self.connection.commit()

    def fetchone(
        self,
        query: str,
        params: tuple[Any, ...] | None = None,
    ) -> Any:
        """Execute a query and return one row."""

        if self.cursor is None:
            raise RuntimeError("Database is not connected.")

        self.cursor.execute(query, params)

        return self.cursor.fetchone()

    def fetchall(
        self,
        query: str,
        params: tuple[Any, ...] | None = None,
    ) -> list[Any]:
        """Execute a query and return all rows."""

        if self.cursor is None:
            raise RuntimeError("Database is not connected.")

        self.cursor.execute(query, params)

        return self.cursor.fetchall()
