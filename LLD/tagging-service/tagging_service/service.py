"""Tenant-bound application service; each public operation is one transaction.

The caller is a trusted application boundary. Tenant scoping is not authentication.
SQL stays here deliberately: the transaction spans multiple entities, and a generic
CRUD repository would hide the concurrency rules that this example teaches.
"""

import hashlib
import json
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
    # LOCAL LLD: SQLite maintains both lookup directions atomically. A production
    # DynamoDB adapter needs conditional writes and an eventually consistent GSI;
    # it cannot silently preserve every SQLite snapshot/transaction guarantee.
    def __init__(self, database: Database, tenant_id: str):
        """Bind a database and validated tenant identity supplied by a trusted caller.

        Called by: Application startup or per-tenant request composition.
        Returns: None; construction produces TaggingService.
        Example: service = TaggingService(db, "tenant-a") after db.initialize().
        """
        self._database = database
        self._tenant_id = identifier(tenant_id, "tenant_id")

    def _resource_values(self, resource: ResourceKey) -> tuple[str, ...]:
        """Validate a ResourceKey and prepend the service tenant for SQL parameters.

        Called by: Resource read/mutation methods.
        Returns: Tuple (tenant, product, type, resource_id).
        Example: For tenant-a and ResourceKey("jira", "issue", "1"), the tuple has four strings.
        """
        if not isinstance(resource, ResourceKey):
            raise ValidationError("resource must be a ResourceKey")
        return (self._tenant_id, *resource.values())

    def _tag(self, connection: sqlite3.Connection, tag_id: str) -> Tag:
        """Load tag metadata inside the caller's transaction and tenant scope.

        Called by: get_tag and mutation validation.
        Returns: Tag; absent tag raises NotFound.
        Example: _tag(connection, tag_id) prevents attaching a nonexistent tag.
        """
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
        """Check a nonnegative expected version against the observed version.

        Called by: rename, delete and replace operations.
        Returns: None; malformed expectation raises ValidationError, mismatch raises Conflict.
        Example: _expected_version(2, 1) raises Conflict.
        """
        if type(expected) is not int or expected < 0:
            raise ValidationError("expected_version must be a nonnegative integer")
        if actual != expected:
            raise Conflict(f"version mismatch: expected {expected}, current {actual}")

    def create_tag(self, name: str) -> Tag:
        """Create or retrieve a normalized tenant-unique tag atomically.

        Called by: Tag creation caller or demo.
        Returns: Immutable Tag; first committed display spelling wins.
        Example: create_tag(" Backend ") and create_tag("backend") return the same identity.

        Additional contract:
        Get-or-create by normalized name. First successful display spelling wins.
        """
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
        """Read one tag's metadata from a transaction snapshot.

        Called by: Caller displaying a known tag.
        Returns: Tag or NotFound exception.
        Example: service.get_tag(tag.tag_id) returns that tenant's metadata.
        """
        with self._database.transaction() as connection:
            return self._tag(connection, tag_id)

    def rename_tag(self, tag_id: str, name: str, *, expected_version: int) -> Tag:
        """Rename with normalized-name uniqueness and optimistic version checking.

        Called by: Edit-tag caller using the last observed tag version.
        Returns: Updated Tag; conflicts raise without partial changes.
        Example: rename_tag(tag.tag_id, "release", expected_version=tag.version).
        """
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
        """Delete only an unused tag at the expected metadata version.

        Called by: Delete-tag caller after detachment.
        Returns: None; used/missing/stale tags raise a domain error.
        Example: delete_tag(tag.tag_id, expected_version=tag.version) removes an unused tag.

        Additional contract:
        Delete unused tags only. Avoid an unbounded global cascade under a lock.
        """
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
        """Insert a version-zero resource row if absent without resetting an existing row.

        Called by: attach_tag and replace_tags inside a write transaction.
        Returns: None.
        Example: First attachment calls this before inserting its assignment.
        """
        connection.execute(
            "INSERT INTO resources (tenant_id, product, resource_type, resource_id) "
            "VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING",
            values,
        )

    def _snapshot(self, connection: sqlite3.Connection, values: tuple[str, ...]) -> ResourceTags:
        """Read assignment version and sorted tag IDs within one transaction.

        Called by: Resource read and mutation methods.
        Returns: ResourceTags; unseen resource gives empty IDs and version 0.
        Example: _snapshot(connection, values) returns the state used for version checking.
        """
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
        """Read a bounded resource membership and version consistently.

        Called by: Display/edit callers before changing assignments.
        Returns: Immutable ResourceTags.
        Example: For an unseen ResourceKey, get_resource_tags(key).version is 0.
        """
        values = self._resource_values(resource)
        with self._database.transaction() as connection:
            return self._snapshot(connection, values)

    def attach_tag(self, resource: ResourceKey, tag_id: str) -> ResourceTags:
        """Attach an existing tag once, respecting the per-resource cap.

        Called by: Caller adding a resource label.
        Returns: Committed ResourceTags; duplicate attachment leaves version unchanged.
        Example: service.attach_tag(ResourceKey("jira", "issue", "1"), tag.tag_id).
        """
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
        """Remove an assignment if present; missing valid IDs are a no-op.

        Called by: Caller removing a resource label.
        Returns: ResourceTags after the operation.
        Example: Calling detach_tag(key, tag_id) twice only changes version on the first removal.
        """
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
        """Atomically replace membership using a version check and bounded set differences.

        Called by: Bulk-edit caller holding a resource snapshot version.
        Returns: ResourceTags; invalid/missing IDs or stale versions roll back.
        Example: replace_tags(key, [tag.tag_id], expected_version=0) initializes an unseen resource.

        Additional contract:
        Bounded atomic replacement; stale callers must re-read and reconcile.
        """
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
        """Read a bounded tenant tag page ordered by stable tag ID.

        Called by: Tag browsing caller.
        Returns: Page[Tag] with items and optional next_cursor.
        Example: page = service.list_tags(limit=2); pass page.next_cursor for the next page.
        """
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

    def search_tags(self, prefix: str, *, limit: int = 50, cursor: str | None = None) -> Page[Tag]:
        """Search a normalized literal name prefix using indexed range conditions.

        Called by: Autocomplete or tag browsing caller.
        Returns: Page[Tag] ordered by normalized name then ID.
        Example: search_tags("rel", limit=10) finds release-like names, not arbitrary substrings.

        Additional contract:
        Literal normalized prefix search, ordered by normalized name then ID.
        """
        _, normalized = tag_name(prefix)
        limit = page_size(limit)
        scope = [self._tenant_id, "tag-prefix", normalized]
        after = decode_cursor(cursor, scope, 2) or ["", ""]
        # Compute the lexicographic exclusive upper bound, avoiding LIKE wildcard
        # semantics. The existing tenant/name unique index supports this range.
        upper = normalized[:-1] + chr(ord(normalized[-1]) + 1)
        with self._database.transaction() as connection:
            rows = connection.execute(
                "SELECT tag_id, display_name, version, normalized_name FROM tags "
                "WHERE tenant_id=? AND normalized_name>=? AND normalized_name<? "
                "AND (normalized_name, tag_id) > (?, ?) "
                "ORDER BY normalized_name, tag_id LIMIT ?",
                (self._tenant_id, normalized, upper, *after, limit + 1),
            ).fetchall()
        items = tuple(
            Tag(row["tag_id"], row["display_name"], row["version"]) for row in rows[:limit]
        )
        next_cursor = None
        if len(rows) > limit:
            last = rows[limit - 1]
            next_cursor = encode_cursor(scope, [last["normalized_name"], last["tag_id"]])
        return Page(items, next_cursor)

    def find_resources(
        self,
        tag_ids: Iterable[str],
        *,
        match: str = "all",
        product: str | None = None,
        resource_type: str | None = None,
        limit: int = 50,
        cursor: str | None = None,
    ) -> Page[ResourceKey]:
        """Find tenant resources matching ALL or ANY requested tags and optional product/type.

        Called by: Boolean-search caller.
        Returns: Page[ResourceKey]; missing tags act as empty sets.
        Example: find_resources([a, b], match="all", product="jira") returns Jira resources with both IDs.

        Additional contract:
        Find resources matching all/any of 1-20 tags with query-bound pagination.

        Missing tag IDs are treated as empty sets. Result size is bounded; SQL
        aggregation work still grows with matching assignments, not page size.
        """
        if isinstance(tag_ids, (str, bytes)) or not isinstance(tag_ids, Iterable):
            raise ValidationError("tag_ids must be an iterable of tag IDs")
        requested = set()
        for count, tag_id in enumerate(tag_ids, start=1):
            if count > 20:
                raise ValidationError("search accepts at most 20 input tags")
            requested.add(identifier(tag_id, "tag_id"))
        if not requested or match not in ("all", "any"):
            raise ValidationError("search requires tags and match='all' or 'any'")
        for value, field in ((product, "product"), (resource_type, "resource_type")):
            if value is not None:
                identifier(value, field)
        limit = page_size(limit)
        ordered_tags = sorted(requested)
        query_hash = hashlib.sha256(
            json.dumps([ordered_tags, match, product, resource_type]).encode()
        ).hexdigest()
        scope = [self._tenant_id, "multi-tag", query_hash]
        after = decode_cursor(cursor, scope, 3) or ["", "", ""]
        placeholders = ",".join("?" for _ in ordered_tags)
        filters = ["tenant_id=?", f"tag_id IN ({placeholders})"]
        parameters = [self._tenant_id, *ordered_tags]
        for value, field in ((product, "product"), (resource_type, "resource_type")):
            if value is not None:
                filters.append(f"{field}=?")
                parameters.append(value)
        filters.append("(product, resource_type, resource_id) > (?, ?, ?)")
        parameters.extend(after)
        having = " HAVING COUNT(*)=?" if match == "all" else ""
        if match == "all":
            parameters.append(len(ordered_tags))
        parameters.append(limit + 1)
        # PRODUCTION SCALE: a reverse DynamoDB GSI can query one tag, but cannot
        # perform this SQL intersection. Use bounded candidate verification or a
        # search projection for expensive Boolean queries. Hot tags require
        # bucketed keys, per-bucket cursor progress and a stated staleness policy.
        with self._database.transaction() as connection:
            rows = connection.execute(
                "SELECT product, resource_type, resource_id FROM assignments WHERE "
                + " AND ".join(filters)
                + " GROUP BY product, resource_type, resource_id"
                + having
                + " ORDER BY product, resource_type, resource_id LIMIT ?",
                parameters,
            ).fetchall()
        items = tuple(ResourceKey(**dict(row)) for row in rows[:limit])
        next_cursor = encode_cursor(scope, list(items[-1].values())) if len(rows) > limit else None
        return Page(items, next_cursor)

    def list_resources(
        self, tag_id: str, *, limit: int = 50, cursor: str | None = None
    ) -> Page[ResourceKey]:
        """Read a tag's reverse associations with a composite seek cursor.

        Called by: Caller opening a tag's resource list.
        Returns: Page[ResourceKey]; nonexistent tag raises NotFound.
        Example: list_resources(tag.tag_id, limit=20) returns at most twenty resource keys.
        """
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
