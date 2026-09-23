"""Connection/transaction boundary. Each operation owns one connection."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS tags (
    tenant_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 0 CHECK(version >= 0),
    PRIMARY KEY (tenant_id, tag_id),
    UNIQUE (tenant_id, normalized_name)
);
CREATE TABLE IF NOT EXISTS resources (
    tenant_id TEXT NOT NULL,
    product TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 0 CHECK(version >= 0),
    PRIMARY KEY (tenant_id, product, resource_type, resource_id)
);
CREATE TABLE IF NOT EXISTS assignments (
    tenant_id TEXT NOT NULL,
    product TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    PRIMARY KEY (tenant_id, product, resource_type, resource_id, tag_id),
    FOREIGN KEY (tenant_id, product, resource_type, resource_id)
        REFERENCES resources (tenant_id, product, resource_type, resource_id),
    FOREIGN KEY (tenant_id, tag_id) REFERENCES tags (tenant_id, tag_id)
);
CREATE INDEX IF NOT EXISTS assignments_by_tag
    ON assignments (tenant_id, tag_id, product, resource_type, resource_id);
"""


class Database:
    # LOCAL LLD: one SQLite file, no external server. Adding HTTP replicas alone
    # will not remove the single-writer limit. Production needs a shared backend,
    # request admission/rate limits, deadlines, telemetry and load-tested capacity.
    def __init__(self, path: str | Path, *, busy_timeout_seconds: float = 5.0):
        """Validate and store a local file path and lock timeout; does not open/create the schema.

        Called by: Startup code, demos and test fixtures.
        Returns: None; construction produces Database.
        Example: Database("tags.sqlite3", busy_timeout_seconds=2) configures a two-second lock wait.
        """
        if str(path) == ":memory:":
            raise ValueError("Use a file database: operations use independent connections")
        if not 0 < busy_timeout_seconds <= 60:
            raise ValueError("busy_timeout_seconds must be in (0, 60]")
        self.path = str(Path(path).resolve())
        self.busy_timeout_seconds = busy_timeout_seconds

    def _connect(self) -> sqlite3.Connection:
        """Open one connection with foreign keys, row mapping and full synchronization.

        Called by: initialize and transaction.
        Returns: New sqlite3.Connection owned by the caller.
        Example: transaction() calls this once per operation and later closes it.
        """
        connection = sqlite3.connect(
            self.path, timeout=self.busy_timeout_seconds, isolation_level=None
        )
        try:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("PRAGMA synchronous = FULL")
        except BaseException:
            connection.close()
            raise
        return connection

    def initialize(self) -> None:
        """Enable WAL and create missing schema objects; this is bootstrap, not migration.

        Called by: Startup before constructing/using the service.
        Returns: None; SQLite failures propagate.
        Example: db.initialize() prepares tables before service.create_tag("release").

        Additional contract:
        Call once during startup, before accepting requests.
        """
        connection = self._connect()
        try:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.executescript(SCHEMA)
        finally:
            connection.close()

    @contextmanager
    def transaction(self, *, write: bool = False) -> Iterator[sqlite3.Connection]:
        """Own a connection and commit on success or roll back on exceptions.

        Called by: Service methods through a with block.
        Returns: Context manager yielding sqlite3.Connection; always closes it.
        Example: with db.transaction(write=True) as connection: connection.execute(sql, params).
        """
        connection = self._connect()
        try:
            # Acquire the write reservation BEFORE reading versions or membership.
            connection.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()
