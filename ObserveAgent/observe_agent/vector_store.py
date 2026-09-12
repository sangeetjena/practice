"""Chroma vector retrieval backed by the SQLite source archive and incident audit."""

import hashlib
import json

import chromadb

from .knowledge import SQLiteKnowledgeStore
from .models import SearchHit


class ChromaKnowledgeStore(SQLiteKnowledgeStore):
    def __init__(self, path, embedder, chroma_path):
        super().__init__(path, embedder)
        self.client = chromadb.PersistentClient(path=str(chroma_path))
        profile = hashlib.sha256(embedder.profile.encode()).hexdigest()[:24]
        self.collection = self.client.get_or_create_collection(
            name=f"knowledge-{profile}",
            embedding_function=None,
            metadata={"hnsw:space": "cosine"},
        )

    def ingest(self, source_id, text, metadata, chunker=None):
        ids = super().ingest(source_id, text, metadata, chunker)
        self._sync_source(source_id)
        return ids

    def _sync_source(self, source_id):
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM knowledge_chunks WHERE source_id=? AND active=1 "
                "AND embedding_profile=?",
                (source_id, self.embedder.profile),
            ).fetchall()
        if rows:
            self.collection.upsert(
                ids=[r["id"] for r in rows],
                documents=[r["content"] for r in rows],
                embeddings=[json.loads(r["embedding"]) for r in rows],
                metadatas=[{**json.loads(r["metadata"]), "source_id": source_id} for r in rows],
            )

    def search(self, query, *, tenant_id, service, limit=5):
        # Archive IDs fence stale Chroma records after document replacement or partial sync.
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id FROM knowledge_chunks WHERE active=1 AND embedding_profile=?",
                (self.embedder.profile,),
            ).fetchall()
        ids = [r["id"] for r in rows]
        if not ids or not self.collection.count():
            return []
        result = self.collection.query(
            query_embeddings=[self.embedder.embed(query)],
            ids=ids,
            n_results=limit,
            where={
                "$and": [
                    {"tenant_scope": {"$in": ["global", tenant_id]}},
                    {"service": {"$in": ["all", service]}},
                    {"review_status": "approved"},
                ]
            },
        )
        return [
            SearchHit(
                chunk_id=chunk_id,
                source_id=metadata["source_id"],
                content=content,
                metadata=metadata,
                score=1 - distance,
            )
            for chunk_id, metadata, content, distance in zip(
                result["ids"][0],
                result["metadatas"][0],
                result["documents"][0],
                result["distances"][0],
                strict=True,
            )
        ]

    def reindex(self):
        count = super().reindex()
        with self._connect() as connection:
            sources = connection.execute(
                "SELECT DISTINCT source_id FROM knowledge_chunks WHERE active=1"
            ).fetchall()
        for source in sources:
            self._sync_source(source["source_id"])
        return count
