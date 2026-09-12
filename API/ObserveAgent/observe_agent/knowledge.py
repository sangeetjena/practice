"""Chunking, deterministic embeddings, hybrid retrieval, and versioned feedback storage."""

from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Protocol

from .models import (
    Incident,
    IncidentFeatures,
    IncidentFeedback,
    KnowledgeChunk,
    SearchHit,
    TriageReport,
    utc_now,
)

TOKEN_RE = re.compile(r"[A-Za-z0-9_.:-]+")


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> list[float]: ...


class HashEmbedding:
    """Offline, deterministic feature hashing for a runnable lab.

    It is useful for tests and architecture learning, not a replacement for a production semantic
    embedding model. Exact-token retrieval is also used so error codes remain findable.
    """

    def __init__(self, dimensions: int = 128) -> None:
        if dimensions < 16:
            raise ValueError("dimensions must be at least 16")
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token, count in Counter(_tokens(text)).items():
            digest = hashlib.sha256(token.encode()).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1 if digest[4] % 2 == 0 else -1
            vector[bucket] += sign * (1 + math.log(count))
        norm = math.sqrt(sum(value * value for value in vector)) or 1
        return [value / norm for value in vector]


class MarkdownChunker:
    """Split Markdown on headings, then enforce a bounded chunk size."""

    def __init__(self, max_chars: int = 1_200) -> None:
        if max_chars < 200:
            raise ValueError("max_chars must be at least 200")
        self.max_chars = max_chars

    def split(self, text: str) -> list[tuple[str, dict[str, Any]]]:
        sections: list[tuple[str, list[str]]] = []
        heading = "Overview"
        lines: list[str] = []
        for line in text.splitlines():
            if line.startswith("#"):
                if any(item.strip() for item in lines):
                    sections.append((heading, lines))
                heading = line.lstrip("#").strip() or "Untitled"
                lines = []
            else:
                lines.append(line)
        if any(item.strip() for item in lines):
            sections.append((heading, lines))

        chunks: list[tuple[str, dict[str, Any]]] = []
        for section, body_lines in sections:
            paragraphs = [item.strip() for item in "\n".join(body_lines).split("\n\n") if item.strip()]
            current = f"# {section}\n"
            part = 1
            for paragraph in paragraphs:
                addition = paragraph + "\n\n"
                if len(current) + len(addition) > self.max_chars and len(current.strip()) > len(section) + 2:
                    chunks.append((current.strip(), {"section": section, "part": part}))
                    part += 1
                    current = f"# {section}\n{addition}"
                else:
                    current += addition
            if current.strip() != f"# {section}":
                chunks.append((current.strip(), {"section": section, "part": part}))
        return chunks


class SQLiteKnowledgeStore:
    """Small persistent hybrid vector store and incident audit database."""

    def __init__(self, path: str | Path, embedder: EmbeddingProvider | None = None) -> None:
        self.path = str(path)
        self.embedder = embedder or HashEmbedding()
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS knowledge_chunks (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1
                );
                CREATE INDEX IF NOT EXISTS knowledge_source_idx
                    ON knowledge_chunks(source_id, active);
                CREATE TABLE IF NOT EXISTS incidents (
                    id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS reports (
                    incident_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS incident_features (
                    incident_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def ingest(
        self,
        source_id: str,
        text: str,
        metadata: dict[str, Any],
        chunker: MarkdownChunker | None = None,
    ) -> list[str]:
        splitter = chunker or MarkdownChunker()
        pieces = splitter.split(text)
        now = utc_now()
        ids: list[str] = []
        with self._connect() as connection:
            prior = connection.execute(
                "SELECT COALESCE(MAX(version), 0) AS version FROM knowledge_chunks WHERE source_id = ?",
                (source_id,),
            ).fetchone()["version"]
            version = int(prior) + 1
            connection.execute(
                "UPDATE knowledge_chunks SET active = 0 WHERE source_id = ?",
                (source_id,),
            )
            for position, (content, chunk_metadata) in enumerate(pieces):
                chunk_id = hashlib.sha256(
                    f"{source_id}:{version}:{position}:{content}".encode()
                ).hexdigest()[:24]
                combined_metadata = {**metadata, **chunk_metadata}
                chunk = KnowledgeChunk(
                    id=chunk_id,
                    source_id=source_id,
                    content=content,
                    metadata=combined_metadata,
                    embedding=self.embedder.embed(content),
                    version=version,
                    created_at=now,
                )
                connection.execute(
                    """
                    INSERT INTO knowledge_chunks
                        (id, source_id, content, embedding, metadata, version, created_at, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    """,
                    (
                        chunk.id,
                        chunk.source_id,
                        chunk.content,
                        json.dumps(chunk.embedding),
                        json.dumps(chunk.metadata, sort_keys=True),
                        chunk.version,
                        chunk.created_at.isoformat(),
                    ),
                )
                ids.append(chunk_id)
        return ids

    def has_active_source(self, source_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM knowledge_chunks WHERE source_id = ? AND active = 1 LIMIT 1",
                (source_id,),
            ).fetchone()
        return row is not None

    def search(
        self,
        query: str,
        *,
        tenant_id: str,
        service: str,
        limit: int = 5,
    ) -> list[SearchHit]:
        query_embedding = self.embedder.embed(query)
        query_tokens = set(_tokens(query))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM knowledge_chunks WHERE active = 1"
            ).fetchall()
        hits: list[SearchHit] = []
        for row in rows:
            metadata = json.loads(row["metadata"])
            scope = metadata.get("tenant_scope", "global")
            if scope not in {"global", tenant_id}:
                continue
            document_service = metadata.get("service", "all")
            if document_service not in {"all", service}:
                continue
            if metadata.get("review_status", "approved") != "approved":
                continue
            content_tokens = set(_tokens(row["content"]))
            lexical = len(query_tokens & content_tokens) / max(1, len(query_tokens | content_tokens))
            cosine = _dot(query_embedding, json.loads(row["embedding"]))
            authority = 0.05 if metadata.get("source_type") == "runbook" else 0.0
            score = 0.65 * cosine + 0.30 * lexical + authority
            hits.append(
                SearchHit(
                    chunk_id=row["id"],
                    source_id=row["source_id"],
                    content=row["content"],
                    metadata=metadata,
                    score=round(score, 6),
                )
            )
        return sorted(hits, key=lambda item: item.score, reverse=True)[:limit]

    def save_incident(self, incident: Incident) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO incidents(id, payload, created_at) VALUES (?, ?, ?)",
                (incident.id, incident.model_dump_json(), utc_now().isoformat()),
            )

    def get_incident(self, incident_id: str) -> Incident | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM incidents WHERE id = ?", (incident_id,)
            ).fetchone()
        return Incident.model_validate_json(row["payload"]) if row else None

    def save_report(self, report: TriageReport) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO reports(incident_id, payload, created_at) VALUES (?, ?, ?)",
                (report.incident_id, report.model_dump_json(), utc_now().isoformat()),
            )

    def save_features(self, features: IncidentFeatures) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO incident_features(incident_id, payload, created_at)
                VALUES (?, ?, ?)
                """,
                (features.incident_id, features.model_dump_json(), utc_now().isoformat()),
            )

    def get_features(self, incident_id: str) -> IncidentFeatures | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM incident_features WHERE incident_id = ?", (incident_id,)
            ).fetchone()
        return IncidentFeatures.model_validate_json(row["payload"]) if row else None

    def get_report(self, incident_id: str) -> TriageReport | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM reports WHERE incident_id = ?", (incident_id,)
            ).fetchone()
        return TriageReport.model_validate_json(row["payload"]) if row else None

    def save_feedback(self, incident_id: str, feedback: IncidentFeedback) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO feedback(incident_id, payload, created_at) VALUES (?, ?, ?)",
                (incident_id, feedback.model_dump_json(), utc_now().isoformat()),
            )


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def _dot(left: Iterable[float], right: Iterable[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=False))
