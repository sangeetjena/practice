"""Tenant-scoped persistence. PostgreSQL in Compose/K8s; SQLite for isolated tests."""
import hashlib
import json
import uuid

from fastapi import HTTPException
from sqlalchemy import Column, Integer, MetaData, String, Table, Text, create_engine, select, text
from sqlalchemy.exc import IntegrityError

metadata = MetaData()
records = Table("records", metadata,
                Column("tenant", String(80), primary_key=True),
                Column("kind", String(30), primary_key=True),
                Column("id", String(80), primary_key=True), Column("payload", Text, nullable=False))
keys = Table("idempotency", metadata,
             Column("tenant", String(80), primary_key=True),
             Column("key", String(128), primary_key=True),
             Column("fingerprint", String(64), nullable=False),
             Column("response", Text, nullable=False), Column("status", Integer, nullable=False))


class Store:
    def __init__(self, url):
        self.engine = create_engine(url, pool_pre_ping=True)

    def initialize(self, kind):
        # Run once as a release job, never concurrently from each application pod.
        metadata.create_all(self.engine)
        with self.engine.begin() as conn:
            for tenant in ("acme", "globex"):
                for i in range(1, 16):
                    item = {"id": f"{kind}-{i:03}", "name": f"{tenant} {kind} sample {i}"}
                    if kind == "orders":
                        item.update(customer_id=f"customers-{i:03}", product_id=f"products-{i:03}",
                                    quantity=i, unit_price=10.0)
                    if kind == "products":
                        item.update(unit_price=float(i * 10))
                    exists = conn.execute(select(records.c.id).where(
                        records.c.tenant == tenant, records.c.kind == kind,
                        records.c.id == item["id"])).first()
                    if not exists:
                        conn.execute(records.insert().values(tenant=tenant, kind=kind,
                                                             id=item["id"], payload=json.dumps(item)))

    def ready(self):
        with self.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.execute(select(records.c.id).limit(1))

    def page(self, tenant, kind, after, limit):
        with self.engine.connect() as conn:
            rows = conn.execute(select(records.c.payload).where(
                records.c.tenant == tenant, records.c.kind == kind, records.c.id > after
            ).order_by(records.c.id).limit(limit + 1)).scalars().all()
        return [json.loads(row) for row in rows]

    def get(self, tenant, kind, item_id):
        with self.engine.connect() as conn:
            row = conn.execute(select(records.c.payload).where(
                records.c.tenant == tenant, records.c.kind == kind,
                records.c.id == item_id)).scalar_one_or_none()
        if row is None:
            raise HTTPException(404, "Resource not found")
        return json.loads(row)

    def create_order(self, tenant, key, payload):
        fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        result = {"id": f"orders-{uuid.uuid4().hex}", **payload}
        try:
            with self.engine.begin() as conn:
                conn.execute(keys.insert().values(tenant=tenant, key=key, fingerprint=fingerprint,
                                                  response=json.dumps(result), status=201))
                conn.execute(records.insert().values(tenant=tenant, kind="orders", id=result["id"],
                                                     payload=json.dumps(result)))
            return result
        except IntegrityError:
            with self.engine.connect() as conn:
                existing = conn.execute(select(keys).where(
                    keys.c.tenant == tenant, keys.c.key == key)).mappings().one_or_none()
            if not existing:
                raise
            if existing["fingerprint"] != fingerprint:
                raise HTTPException(409, "Idempotency key reused with a different payload") from None
            return json.loads(existing["response"])


jobs = Table("import_jobs", metadata,
             Column("tenant", String(80), primary_key=True),
             Column("id", String(80), primary_key=True),
             Column("key", String(128), nullable=False),
             Column("fingerprint", String(64), nullable=False),
             Column("payload", Text, nullable=False),
             Column("state", String(20), nullable=False),
             Column("lease", Integer, nullable=False),
             Column("claim", String(80), nullable=False),
             Column("attempts", Integer, nullable=False),
             Column("result", Text, nullable=False))
# Separate operation-specific uniqueness; a create-order key cannot collide with an import key.
from sqlalchemy import UniqueConstraint

jobs.append_constraint(UniqueConstraint("tenant", "key"))


def submit_job(store, tenant, key, payload):
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    job_id = uuid.uuid4().hex
    try:
        with store.engine.begin() as conn:
            conn.execute(jobs.insert().values(tenant=tenant, id=job_id, key=key,
                         fingerprint=fingerprint, payload=json.dumps(payload), state="pending",
                         lease=0, claim="", attempts=0, result="{}"))
    except IntegrityError:
        with store.engine.connect() as conn:
            row = conn.execute(select(jobs).where(jobs.c.tenant == tenant,
                               jobs.c.key == key)).mappings().one()
        if row["fingerprint"] != fingerprint:
            raise HTTPException(409, "Idempotency key reused with a different import") from None
        job_id = row["id"]
    return read_job(store, tenant, job_id)


def read_job(store, tenant, job_id):
    with store.engine.connect() as conn:
        row = conn.execute(select(jobs).where(jobs.c.tenant == tenant,
                           jobs.c.id == job_id)).mappings().one_or_none()
    if row is None:
        raise HTTPException(404, "Job not found")
    return {"id": row["id"], "state": row["state"], "attempts": row["attempts"],
            "result": json.loads(row["result"])}
