"""Tenant-bound PostgreSQL archive and remote Chroma retrieval adapter.

Example: TenantKnowledge(db, client, embedder, 'acme') cannot read Globex records.
Each tenant/profile has a separate Chroma collection; active archive IDs additionally
fence stale versions. `reindex()` repairs partial publication and model changes.
"""

import hashlib
import uuid

from sqlalchemy import and_, select

from ..knowledge import MarkdownChunker
from ..models import ActionResult, Incident, IncidentFeatures, SearchHit, TriageReport
from .database import records


class TenantKnowledge:
    def __init__(self, db, client, embedder, tenant_id):
        self.db, self.embedder, self.tenant_id = db, embedder, tenant_id
        name = hashlib.sha256(f"{tenant_id}:{embedder.profile}".encode()).hexdigest()[:32]
        self.collection = client.get_or_create_collection(
            name=f"knowledge-{name}",
            embedding_function=None,
            metadata={"hnsw:space": "cosine"},
        )

    def _get(self, kind, key, model=None):
        value = self.db.record_get(self.tenant_id, kind, key)
        return model.model_validate(value) if model and value is not None else value

    def _put(self, kind, key, value):
        if hasattr(value, "model_dump"):
            value = value.model_dump(mode="json")
        self.db.record_put(self.tenant_id, kind, key, value)

    def save_incident(self, incident):
        if incident.tenant_id != self.tenant_id:
            raise ValueError("tenant mismatch")
        self._put("incident", incident.id, incident)

    def get_incident(self, key):
        return self._get("incident", key, Incident)

    def save_features(self, features):
        self._put("features", features.incident_id, features)

    def get_features(self, key):
        return self._get("features", key, IncidentFeatures)

    def save_report(self, report):
        self._put("report", report.incident_id, report)

    def get_report(self, key):
        return self._get("report", key, TriageReport)

    def save_feedback(self, key, feedback):
        # Content-based ID makes event replay audit-idempotent.
        from .database import fingerprint

        self._put("feedback", fingerprint([key, feedback.model_dump(mode="json")]), feedback)

    def save_action_proposal(self, action):
        self._put("action_proposal", action.id, action)

    def get_action_result(self, key):
        return self._get("action_result", key, ActionResult)

    def save_action_result(self, result):
        self._put("action_result", result.action_id, result)

    def has_active_source(self, source_id):
        return self._get("knowledge", source_id) is not None

    def ingest(self, source_id, text, metadata, chunker=None):
        if metadata.get("tenant_scope") not in {None, self.tenant_id}:
            raise ValueError("cloud knowledge ingestion must be tenant-scoped")
        pieces = (chunker or MarkdownChunker()).split(text)
        chunks = [
            {
                "id": str(uuid.uuid4()),
                "content": content,
                "embedding": self.embedder.embed(content),
                "metadata": {
                    **metadata,
                    **section,
                    "tenant_scope": self.tenant_id,
                    "source_id": source_id,
                },
            }
            for content, section in pieces
        ]
        payload = {"source_id": source_id, "profile": self.embedder.profile, "chunks": chunks}
        version_id = hashlib.sha256(f"{source_id}:{uuid.uuid4()}".encode()).hexdigest()
        self._put("knowledge_version", version_id, payload)
        self._put("knowledge", source_id, payload)
        self.sync_source(source_id)
        return [c["id"] for c in chunks]

    def sync_source(self, source_id):
        source = self._get("knowledge", source_id)
        if source is None or source["profile"] != self.embedder.profile:
            return
        chunks = source["chunks"]
        if chunks:
            self.collection.upsert(
                ids=[c["id"] for c in chunks],
                documents=[c["content"] for c in chunks],
                embeddings=[c["embedding"] for c in chunks],
                metadatas=[c["metadata"] for c in chunks],
            )

    def _sources(self):
        with self.db.engine.connect() as conn:
            return (
                conn.execute(
                    select(records.c.payload).where(
                        and_(
                            records.c.tenant_id == self.tenant_id,
                            records.c.kind == "knowledge",
                        )
                    )
                )
                .scalars()
                .all()
            )

    def search(self, query, *, tenant_id, service, limit=5):
        if tenant_id != self.tenant_id:
            raise ValueError("tenant mismatch")
        ids = [
            c["id"]
            for s in self._sources()
            if s["profile"] == self.embedder.profile
            for c in s["chunks"]
            if c["metadata"].get("review_status") == "approved"
            and c["metadata"].get("service") in {"all", service}
        ]
        if not ids or not self.collection.count():
            return []
        result = self.collection.query(
            query_embeddings=[self.embedder.embed(query)],
            ids=ids,
            n_results=min(limit, len(ids)),
            where={"tenant_scope": self.tenant_id},
        )
        return [
            SearchHit(chunk_id=i, source_id=m["source_id"], content=c, metadata=m, score=1 - d)
            for i, m, c, d in zip(
                result["ids"][0],
                result["metadatas"][0],
                result["documents"][0],
                result["distances"][0],
                strict=True,
            )
        ]

    def reindex(self):
        count = 0
        for source in self._sources():
            for chunk in source["chunks"]:
                chunk["embedding"] = self.embedder.embed(chunk["content"])
                count += 1
            source["profile"] = self.embedder.profile
            self._put("knowledge", source["source_id"], source)
            self.sync_source(source["source_id"])
        return count
