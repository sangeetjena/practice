"""Tenant-bound application service; each public operation is one transaction.

The caller is a trusted application boundary. Tenant scoping is not authentication.
SQL stays here deliberately: the transaction spans multiple entities, and a generic
CRUD repository would hide the concurrency rules that this example teaches.
"""

import sqlite3
from collections.abc import Iterable
from uuid import uuid4

from .database import Database
from .models import (
    Conflict,
    NotFound,
    Page,
    ResourceKey,
    ResourceTags,
    Tag,
    ValidationError,
    identifier,
    tag_name,
)
from .pagination import decode_cursor, encode_cursor, page_size

RESOURCE_FILTER = "tenant_id=? AND product=? AND resource_type=? AND resource_id=?"
MAX_TAGS_PER_RESOURCE = 1000


class TaggingService:
    def __init__(self, database: Database, tenant_id: str):
        self._database = database
        self._tenant_id = identifier(tenant_id, "tenant_id")

    def _resource_values(self, resource: ResourceKey) -> tuple[str, ...]:
        if not isinstance(resource, ResourceKey):
            raise ValidationError("resource must be a ResourceKey")
        return (self._tenant_id, *resource.values())

    def _tag(self, connection: sqlite3.Connection, tag_id: str) -> Tag:
        identifier(tag_id, "tag_id")
        row = connection.execute(
            "SELECT tag_id, display_name, version FROM tags WHERE tenant_id=? AND tag_id=?",
            (self._tenant_id, tag_id),
        ).fetchone()
        if row is None:
            raise NotFound("tag not found")
        return Tag(**dict(row))

    @staticmethod
    def _expected_version(actual: int, expected: int) -> None:
        if type(expected) is not int or expected < 0:
            raise ValidationError("expected_version must be a nonnegative integer")
        if actual != expected:
            raise Conflict(f"version mismatch: expected {expected}, current {actual}")

    def create_tag(self, name: str) -> Tag:
        """Get-or-create by normalized name. First successful display spelling wins."""
        display, normalized = tag_name(name)
        with self._database.transaction(write=True) as connection:
            connection.execute(
                "INSERT INTO tags (tenant_id, tag_id, normalized_name, display_name) "
                "VALUES (?, ?, ?, ?) ON CONFLICT(tenant_id, normalized_name) DO NOTHING",
                (self._tenant_id, uuid4().hex, normalized, display),
            )
            row = connection.execute(
                "SELECT tag_id, display_name, version FROM tags "
                "WHERE tenant_id=? AND normalized_name=?",
                (self._tenant_id, normalized),
            ).fetchone()
            return Tag(**dict(row))

    def get_tag(self, tag_id: str) -> Tag:
        with self._database.transaction() as connection:
            return self._tag(connection, tag_id)

    def rename_tag(self, tag_id: str, name: str, *, expected_version: int) -> Tag:
        display, normalized = tag_name(name)
        with self._database.transaction(write=True) as connection:
            tag = self._tag(connection, tag_id)
            self._expected_version(tag.version, expected_version)
            if tag.display_name == display:
                return tag
            try:
                connection.execute(
                    "UPDATE tags SET display_name=?, normalized_name=?, version=version+1 "
                    "WHERE tenant_id=? AND tag_id=?",
                    (display, normalized, self._tenant_id, tag_id),
                )
            except sqlite3.IntegrityError as error:
                raise Conflict("tag name already exists") from error
            return Tag(tag_id, display, tag.version + 1)

    def delete_tag(self, tag_id: str, *, expected_version: int) -> None:
        """Delete unused tags only. Avoid an unbounded global cascade under a lock."""
        with self._database.transaction(write=True) as connection:
            tag = self._tag(connection, tag_id)
            self._expected_version(tag.version, expected_version)
            used = connection.execute(
                "SELECT 1 FROM assignments WHERE tenant_id=? AND tag_id=? LIMIT 1",
                (self._tenant_id, tag_id),
            ).fetchone()
            if used:
                raise Conflict("detach tag from resources before deleting it")
            connection.execute(
                "DELETE FROM tags WHERE tenant_id=? AND tag_id=?",
                (self._tenant_id, tag_id),
            )

    def _ensure_resource(self, connection: sqlite3.Connection, values: tuple[str, ...]) -> None:
        connection.execute(
            "INSERT INTO resources (tenant_id, product, resource_type, resource_id) "
            "VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING",
            values,
        )

    def _snapshot(self, connection: sqlite3.Connection, values: tuple[str, ...]) -> ResourceTags:
        row = connection.execute(
            f"SELECT version FROM resources WHERE {RESOURCE_FILTER}",
            values,
        ).fetchone()
        tags = connection.execute(
            f"SELECT tag_id FROM assignments WHERE {RESOURCE_FILTER} ORDER BY tag_id",
            values,
        ).fetchall()
        return ResourceTags(tuple(row["tag_id"] for row in tags), row["version"] if row else 0)

    def get_resource_tags(self, resource: ResourceKey) -> ResourceTags:
        values = self._resource_values(resource)
        with self._database.transaction() as connection:
            return self._snapshot(connection, values)

    def attach_tag(self, resource: ResourceKey, tag_id: str) -> ResourceTags:
        values = self._resource_values(resource)
        with self._database.transaction(write=True) as connection:
            self._tag(connection, tag_id)
            current = self._snapshot(connection, values)
            if tag_id in current.tag_ids:
                return current
            if len(current.tag_ids) >= MAX_TAGS_PER_RESOURCE:
                raise ValidationError("resource tag limit exceeded")
            self._ensure_resource(connection, values)
            connection.execute("INSERT INTO assignments VALUES (?, ?, ?, ?, ?)", (*values, tag_id))
            connection.execute(
                f"UPDATE resources SET version=version+1 WHERE {RESOURCE_FILTER}",
                values,
            )
            return self._snapshot(connection, values)

    def detach_tag(self, resource: ResourceKey, tag_id: str) -> ResourceTags:
        values = self._resource_values(resource)
        identifier(tag_id, "tag_id")
        with self._database.transaction(write=True) as connection:
            deleted = connection.execute(
                f"DELETE FROM assignments WHERE {RESOURCE_FILTER} AND tag_id=?",
                (*values, tag_id),
            ).rowcount
            if deleted:
                connection.execute(
                    f"UPDATE resources SET version=version+1 WHERE {RESOURCE_FILTER}",
                    values,
                )
            return self._snapshot(connection, values)

    def replace_tags(
        self, resource: ResourceKey, tag_ids: Iterable[str], *, expected_version: int
    ) -> ResourceTags:
        """Bounded atomic replacement; stale callers must re-read and reconcile."""
        values = self._resource_values(resource)
        if isinstance(tag_ids, (str, bytes)) or not isinstance(tag_ids, Iterable):
            raise ValidationError("tag_ids must be an iterable of tag IDs")
        desired = set()
        for count, tag_id in enumerate(tag_ids, start=1):
            if count > MAX_TAGS_PER_RESOURCE:
                raise ValidationError("replacement input exceeds 1000 entries")
            desired.add(identifier(tag_id, "tag_id"))
        with self._database.transaction(write=True) as connection:
            current = self._snapshot(connection, values)
            self._expected_version(current.version, expected_version)
            for tag_id in desired:
                self._tag(connection, tag_id)
            previous = set(current.tag_ids)
            if desired == previous:
                return current
            self._ensure_resource(connection, values)
            connection.executemany(
                f"DELETE FROM assignments WHERE {RESOURCE_FILTER} AND tag_id=?",
                [(*values, tag_id) for tag_id in previous - desired],
            )
            connection.executemany(
                "INSERT INTO assignments VALUES (?, ?, ?, ?, ?)",
                [(*values, tag_id) for tag_id in desired - previous],
            )
            connection.execute(
                f"UPDATE resources SET version=version+1 WHERE {RESOURCE_FILTER}",
                values,
            )
            return self._snapshot(connection, values)

    def list_tags(self, *, limit: int = 50, cursor: str | None = None) -> Page[Tag]:
        limit = page_size(limit)
        scope = [self._tenant_id, "tags"]
        after = decode_cursor(cursor, scope, 1)
        with self._database.transaction() as connection:
            rows = connection.execute(
                "SELECT tag_id, display_name, version FROM tags WHERE tenant_id=? AND tag_id>? "
                "ORDER BY tag_id LIMIT ?",
                (self._tenant_id, after[0] if after else "", limit + 1),
            ).fetchall()
        items = tuple(Tag(**dict(row)) for row in rows[:limit])
        next_cursor = encode_cursor(scope, [items[-1].tag_id]) if len(rows) > limit else None
        return Page(items, next_cursor)

    def list_resources(
        self, tag_id: str, *, limit: int = 50, cursor: str | None = None
    ) -> Page[ResourceKey]:
        identifier(tag_id, "tag_id")
        limit = page_size(limit)
        scope = [self._tenant_id, "resources", tag_id]
        after = decode_cursor(cursor, scope, 3) or ["", "", ""]
        with self._database.transaction() as connection:
            self._tag(connection, tag_id)
            rows = connection.execute(
                "SELECT product, resource_type, resource_id FROM assignments "
                "WHERE tenant_id=? AND tag_id=? AND (product, resource_type, resource_id) > (?, ?, ?) "
                "ORDER BY product, resource_type, resource_id LIMIT ?",
                (self._tenant_id, tag_id, *after, limit + 1),
            ).fetchall()
        items = tuple(ResourceKey(**dict(row)) for row in rows[:limit])
        next_cursor = encode_cursor(scope, list(items[-1].values())) if len(rows) > limit else None
        return Page(items, next_cursor)
