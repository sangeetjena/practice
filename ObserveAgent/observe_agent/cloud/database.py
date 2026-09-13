"""Transactional tenant state, durable outbox and versioned human input.

Example: submit('acme', ...) commits an incident and investigation event together.
The API returns before any LLM call. A worker later claims that event and persists
its result. See docs/modules/database.md for the schema and concurrency walkthrough.
"""

import hashlib
import json
import threading
import time
import uuid
from contextlib import contextmanager

from sqlalchemy import (
    JSON,
    Column,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    and_,
    create_engine,
    insert,
    or_,
    select,
    text,
    update,
)
from sqlalchemy.exc import IntegrityError

metadata = MetaData()
incidents = Table(
    "cloud_incidents",
    metadata,
    Column("tenant_id", String(100), primary_key=True),
    Column("id", String(100), primary_key=True),
    Column("request_key", String(200), nullable=False),
    Column("fingerprint", String(64), nullable=False),
    Column("session_id", String(36), nullable=False),
    Column("run_id", String(36), nullable=False),
    Column("revision", Integer, nullable=False),
    Column("status", String(40), nullable=False),
    Column("payload", JSON, nullable=False),
    Column("result", JSON),
    Column("proposal_version", String(64)),
    UniqueConstraint("tenant_id", "request_key"),
)
events = Table(
    "cloud_events",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("tenant_id", String(100), nullable=False),
    Column("incident_id", String(100), nullable=False),
    Column("kind", String(30), nullable=False),
    Column("run_id", String(36), nullable=False),
    Column("revision", Integer, nullable=False),
    Column("payload", JSON, nullable=False),
    Column("state", String(30), nullable=False),
    Column("attempts", Integer, nullable=False, default=0),
    Column("created_at", Float, nullable=False),
    Column("published_at", Float),
    Column("error", String(200)),
)
messages = Table(
    "cloud_messages",
    metadata,
    Column("tenant_id", String(100), primary_key=True),
    Column("incident_id", String(100), primary_key=True),
    Column("id", String(100), primary_key=True),
    Column("subject", String(200), nullable=False),
    Column("kind", String(30), nullable=False),
    Column("payload", JSON, nullable=False),
    Column("created_at", Float, nullable=False),
)
records = Table(
    "cloud_records",
    metadata,
    Column("tenant_id", String(100), primary_key=True),
    Column("kind", String(40), primary_key=True),
    Column("id", String(200), primary_key=True),
    Column("payload", JSON, nullable=False),
)


def fingerprint(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


class Conflict(ValueError):
    """Request conflicts with an existing submission, run or proposal."""


class Busy(RuntimeError):
    """Another worker owns this incident; delivery should retry."""


class Database:
    def __init__(self, url, *, initialize=False):
        self.engine = create_engine(url, pool_pre_ping=True)
        self._test_locks = {}
        self._lock_guard = threading.Lock()
        if initialize:
            metadata.create_all(self.engine)

    @staticmethod
    def _where(tenant, incident_id):
        return and_(incidents.c.tenant_id == tenant, incidents.c.id == incident_id)

    def get(self, tenant, incident_id, connection=None):
        if connection is None:
            with self.engine.connect() as conn:
                return self.get(tenant, incident_id, conn)
        row = (
            connection.execute(select(incidents).where(self._where(tenant, incident_id)))
            .mappings()
            .first()
        )
        if row is None:
            raise KeyError("incident not found")
        return dict(row)

    def _enqueue(self, conn, row, kind, payload):
        event_id = str(uuid.uuid4())
        conn.execute(
            insert(events).values(
                id=event_id,
                tenant_id=row["tenant_id"],
                incident_id=row["id"],
                kind=kind,
                run_id=row["run_id"],
                revision=row["revision"],
                payload=payload,
                state="pending",
                attempts=0,
                created_at=time.time(),
            )
        )
        return event_id

    def submit(self, tenant, subject, payload, request_key, request_fingerprint):
        row = {
            "tenant_id": tenant,
            "id": payload["id"],
            "request_key": request_key,
            "fingerprint": request_fingerprint,
            "session_id": str(uuid.uuid4()),
            "run_id": str(uuid.uuid4()),
            "revision": 1,
            "status": "queued",
            "payload": payload,
        }
        try:
            with self.engine.begin() as conn:
                conn.execute(insert(incidents).values(**row))
                self._enqueue(conn, row, "investigate", {"subject": subject})
        except IntegrityError:
            with self.engine.connect() as conn:
                existing = (
                    conn.execute(
                        select(incidents).where(
                            and_(
                                incidents.c.tenant_id == tenant,
                                incidents.c.request_key == request_key,
                            )
                        )
                    )
                    .mappings()
                    .first()
                )
                if existing is None or existing["fingerprint"] != request_fingerprint:
                    raise Conflict("incident or idempotency key already used") from None
                return dict(existing)
        return self.get(tenant, payload["id"])

    def append(self, tenant, incident_id, subject, kind, payload):
        """Atomically save input and enqueue it; a stale approval can never pass this gate."""
        with self.engine.begin() as conn:
            row = self.get(tenant, incident_id, conn)
            prior = (
                conn.execute(
                    select(messages).where(
                        and_(
                            messages.c.tenant_id == tenant,
                            messages.c.incident_id == incident_id,
                            messages.c.id == payload["id"],
                        )
                    )
                )
                .mappings()
                .first()
            )
            if prior:
                if (
                    prior["payload"] != payload
                    or prior["kind"] != kind
                    or prior["subject"] != subject
                ):
                    raise Conflict("message ID already used")
                return row
            if row["status"] in {"queued", "running"}:
                raise Conflict("wait for the active event before submitting more input")
            if kind == "feedback" and not row.get("result"):
                raise Conflict("feedback requires an existing investigation result")
            if kind == "approval":
                if (
                    row["status"] != "awaiting_approval"
                    or payload["proposal_version"] != row["proposal_version"]
                ):
                    raise Conflict("approval is stale or incident is not awaiting approval")
                valid = {a["id"] for a in row["result"]["proposed_actions"]}
                if not set(payload["action_ids"]) <= valid:
                    raise Conflict("unknown action IDs")
            old_revision, old_status = row["revision"], row["status"]
            if kind == "message":
                row["revision"] += 1
                row["run_id"] = str(uuid.uuid4())
            changed = conn.execute(
                update(incidents)
                .where(
                    and_(
                        self._where(tenant, incident_id),
                        incidents.c.revision == old_revision,
                        incidents.c.status == old_status,
                    )
                )
                .values(
                    status="queued",
                    revision=row["revision"],
                    run_id=row["run_id"],
                    proposal_version=None,
                )
            )
            if changed.rowcount != 1:
                raise Conflict("incident changed; reload before submitting")
            conn.execute(
                insert(messages).values(
                    tenant_id=tenant,
                    incident_id=incident_id,
                    id=payload["id"],
                    subject=subject,
                    kind=kind,
                    payload=payload,
                    created_at=time.time(),
                )
            )
            self._enqueue(
                conn,
                row,
                kind,
                {**payload, "subject": subject, "previous_result": row.get("result")},
            )
        return self.get(tenant, incident_id)

    def history(self, tenant, incident_id):
        self.get(tenant, incident_id)
        with self.engine.connect() as conn:
            return [
                dict(row)
                for row in conn.execute(
                    select(messages)
                    .where(
                        and_(
                            messages.c.tenant_id == tenant,
                            messages.c.incident_id == incident_id,
                        )
                    )
                    .order_by(messages.c.created_at, messages.c.id)
                ).mappings()
            ]

    def event(self, event_id):
        with self.engine.connect() as conn:
            row = conn.execute(select(events).where(events.c.id == event_id)).mappings().first()
            if row is None:
                raise KeyError("event not found")
            return dict(row)

    def pending(self, limit=100):
        with self.engine.connect() as conn:
            return [
                dict(r)
                for r in conn.execute(
                    select(events)
                    .where(
                        and_(
                            events.c.state.not_in(["done", "dead"]),
                            or_(
                                events.c.published_at.is_(None),
                                events.c.published_at < time.time() - 300,
                            ),
                        )
                    )
                    .order_by(events.c.created_at)
                    .limit(limit)
                ).mappings()
            ]

    def published(self, event_id):
        with self.engine.begin() as conn:
            conn.execute(
                update(events).where(events.c.id == event_id).values(published_at=time.time())
            )

    def start(self, event):
        with self.engine.begin() as conn:
            conn.execute(
                update(events)
                .where(events.c.id == event["id"])
                .values(state="processing", attempts=events.c.attempts + 1)
            )
            conn.execute(
                update(incidents)
                .where(self._where(event["tenant_id"], event["incident_id"]))
                .values(status="running")
            )

    def finish(self, event, result):
        version = fingerprint(
            {"revision": event["revision"], "actions": result.get("proposed_actions", [])}
        )
        with self.engine.begin() as conn:
            conn.execute(
                update(incidents)
                .where(self._where(event["tenant_id"], event["incident_id"]))
                .values(
                    status=result["status"],
                    result=result,
                    proposal_version=version if result["status"] == "awaiting_approval" else None,
                )
            )
            conn.execute(
                update(events).where(events.c.id == event["id"]).values(state="done", error=None)
            )

    def fail(self, event, error, max_attempts):
        terminal = self.event(event["id"])["attempts"] >= max_attempts
        with self.engine.begin() as conn:
            conn.execute(
                update(events)
                .where(events.c.id == event["id"])
                .values(state="dead" if terminal else "pending", error=type(error).__name__)
            )
            conn.execute(
                update(incidents)
                .where(self._where(event["tenant_id"], event["incident_id"]))
                .values(status="failed" if terminal else "queued")
            )
        return terminal

    @contextmanager
    def incident_lock(self, tenant, incident_id):
        """Session advisory lock spans graph execution and releases on connection/process loss.

        No expiring lease lets a second live worker resume the same graph concurrently.
        SQLite fallback is single-process testing only.
        """
        key = int.from_bytes(
            hashlib.sha256(json.dumps([tenant, incident_id]).encode()).digest()[:8],
            "big",
            signed=True,
        )
        if self.engine.dialect.name == "postgresql":
            with self.engine.connect() as conn:
                if not conn.execute(
                    text("SELECT pg_try_advisory_lock(:key)"), {"key": key}
                ).scalar():
                    raise Busy("incident already executing")
                try:
                    yield
                finally:
                    conn.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": key})
        else:
            with self._lock_guard:
                lock = self._test_locks.setdefault(key, threading.Lock())
            if not lock.acquire(blocking=False):
                raise Busy("incident already executing")
            try:
                yield
            finally:
                lock.release()

    def record_get(self, tenant, kind, record_id):
        with self.engine.connect() as conn:
            return conn.execute(
                select(records.c.payload).where(
                    and_(
                        records.c.tenant_id == tenant,
                        records.c.kind == kind,
                        records.c.id == record_id,
                    )
                )
            ).scalar_one_or_none()

    def record_put(self, tenant, kind, record_id, payload):
        dialect = self.engine.dialect.name
        if dialect == "postgresql":
            from sqlalchemy.dialects.postgresql import insert as upsert
        else:
            from sqlalchemy.dialects.sqlite import insert as upsert
        statement = upsert(records).values(
            tenant_id=tenant, kind=kind, id=record_id, payload=payload
        )
        with self.engine.begin() as conn:
            conn.execute(
                statement.on_conflict_do_update(
                    index_elements=["tenant_id", "kind", "id"],
                    set_={"payload": payload},
                )
            )
