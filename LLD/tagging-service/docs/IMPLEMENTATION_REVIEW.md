# Tagging service: implementation and HLD alignment

The executable project is a **standard-library Python + SQLite service library**.
It is a compact persistence/concurrency exercise, not the full distributed HLD.
No HTTP, PostgreSQL, Redis, broker, authorization service or background worker runs
as part of this project. The PostgreSQL schema is a proposed design artifact.

## Implemented and tested

- **Tag catalog:** tenant-scoped get-or-create, get, versioned rename and unused-tag deletion.
- **Assignments:** idempotent attach/detach, bounded atomic replacement and snapshots.
- **Discovery:** tag listing, reverse lookup, literal prefix search and ALL/ANY tag search.
- **Integrity:** composite identities, tenant-scoped uniqueness/foreign keys and parameterized SQL.
- **Concurrency:** one connection per operation, `BEGIN IMMEDIATE` writes, snapshot reads,
  expected-version checks, no-op version preservation and rollback.
- **Persistence:** file-backed SQLite, WAL and `synchronous=FULL`; reopening preserves data.
- **Pagination:** bounded, query-scoped keyset cursors; encoded but **not signed or encrypted**.
- **Contracts:** immutable dataclasses and reusable domain exceptions. `VersionConflict`
  extends `Conflict`; existing exception handlers remain compatible.

## Differences that an HTTP/PostgreSQL implementation must resolve

- **Create:** the library returns an existing normalized name. The HLD proposes strict
  creation with a name conflict plus an idempotency-key replay record. These are different
  contracts; a transport adapter cannot infer a created flag from the returned `Tag`.
- **Delete:** the library hard-deletes only unused tags; a name can then be reused.
  The HLD tombstones used tags immediately, reserves names and cleans assignments later.
- **Resource identity:** the library directly keys resources by `(tenant, product, type,
  external resource_id)`. The HLD introduces an internal UUID and a unique external-key mapping.
- **Versions:** the library starts tag metadata at zero; the PostgreSQL sketch starts at one.
  Versions should be opaque to clients. Membership versions start at zero in both designs.
- **Ordering:** library reverse pages sort by product/type/external ID. The HLD proposes
  `created_at + association_id` for recent-first listing. A change requires new cursor versions.
- **Normalization:** the library explicitly uses NFKC + trim + casefold. The HLD leaves the
  final Unicode policy negotiable. Preserve punctuation such as C++ and C#.
- **Isolation:** SQLite has one writer per file. PostgreSQL requires explicit per-resource
  locking and compatible shared tag locks; changing only the connection string is insufficient.

## Production extensions not implemented

- Verified authentication, product existence/permissions and permission-filtered pagination.
- HTTP routes, ETags, request-id propagation, an error serializer and rate limiting.
- PostgreSQL adapter, migrations, connection pooling, tombstones and resource deletion.
- Transactional outbox, broker delivery, replay/deduplication, search projections and auditing.
- Redis cache-aside, stampede protection, invalidation/version races and degraded-mode limits.
- Signed/expiring caller-bound cursors, metadata hydration and privacy-safe counts.
- Async bulk jobs, generation staging, popularity/trending and multi-region failover.
- Application logging, metrics and tracing. Domain exceptions exist; they are **not** a logging system.

## Public method contracts

### Database and models

- `Database(path, busy_timeout_seconds=5)`: configure a local file; parent directory must exist.
- `initialize()`: enable WAL and bootstrap missing schema; **not a migration engine**.
- `transaction(write=False)`: own a connection, begin, commit/rollback and always close.
- `ResourceKey(product, resource_type, resource_id)`: validate immutable external identity.
- `ResourceKey.values()`: expose the stable SQL/cursor tuple order.
- `Tag`, `ResourceTags`, `Page[T]`: immutable return contracts, now all exported publicly.

### Catalog

```python
create_tag(name: str) -> Tag
get_tag(tag_id: str) -> Tag
rename_tag(tag_id: str, name: str, *, expected_version: int) -> Tag
delete_tag(tag_id: str, *, expected_version: int) -> None
list_tags(*, limit: int = 50, cursor: str | None = None) -> Page[Tag]
search_tags(prefix: str, *, limit: int = 50,
            cursor: str | None = None) -> Page[Tag]
```

Create is normalized get-or-create. Rename preserves identity and assignments;
an unchanged display name is a no-op only after a valid expected-version check.
Delete rejects a used tag. Prefix search is literal, not SQL wildcard matching;
renames can move items between live pages.

### Assignments and resource search

```python
get_resource_tags(resource: ResourceKey) -> ResourceTags
attach_tag(resource: ResourceKey, tag_id: str) -> ResourceTags
detach_tag(resource: ResourceKey, tag_id: str) -> ResourceTags
replace_tags(resource: ResourceKey, tag_ids: Iterable[str],
             *, expected_version: int) -> ResourceTags
list_resources(tag_id: str, *, limit: int = 50,
               cursor: str | None = None) -> Page[ResourceKey]
find_resources(tag_ids: Iterable[str], *, match: str = "all",
               product: str | None = None,
               resource_type: str | None = None,
               limit: int = 50,
               cursor: str | None = None) -> Page[ResourceKey]
```

An unseen resource has empty membership/version zero; it is not externally verified.
Attach requires an existing tag. Detach of an absent valid ID is a no-op.
Replacement checks every desired tag before mutation, then applies set differences.
Retain empty resource rows so versions cannot reset and permit an old writer.
`list_resources` rejects a missing tag; Boolean search treats missing tags as empty sets.
Search accepts 1–20 input entries, replacement at most 1,000; duplicate entries count
toward input limits. Pages contain 1–100 items. Limits bound returned data, not all SQL work.

### Private helpers and pagination

- `_connect`: foreign keys, row factory and full synchronization on each connection.
- `_resource_values`: validate resource and prepend the trusted tenant context.
- `_tag`: tenant-scoped lookup with `NotFound` semantics.
- `_expected_version`: reject malformed expectations; raise `VersionConflict` on mismatch.
- `_ensure_resource`: insert without resetting existing version history.
- `_snapshot`: read version and ordered membership in the same transaction.
- `identifier`, `tag_name`, `page_size`: bounded validation and normalization.
- `encode_cursor`, `decode_cursor`: format/version/query/key checks, **not authentication**.

## Errors and HTTP mapping

The following is a proposed adapter mapping, not a running server:

```python
try:
    result = service.replace_tags(key, tag_ids, expected_version=version)
except VersionConflict:  # subtype before its parent
    status = 412
except Conflict:
    status = 409
except NotFound:
    status = 404
except ValidationError:
    status = 400
```

Map only recognized transient database lock failures to retryable 503. Other database
failures require classification and internal diagnostics, not blind retries or leaked SQL.
Logging at the future transport boundary should include operation, request ID, duration
and error code; avoid raw tag names, resource content or credentials.

## Documentation and verification

The review found docstrings on all 74 original handwritten functions/methods.
The regression test adds one documented method: **75 functions/methods have docstrings**.
Dataclass contracts now also have class documentation. Generated dataclass methods and
anonymous lambdas are not included in that count. Docstrings were checked against method
behavior; presence alone is not proof of correctness.

The original 35 tests passed. The updated **36-test suite** also verifies that stale
rename/delete/replace raises `VersionConflict`, while a duplicate-name conflict remains
plain `Conflict`, with no partial state changes.

```powershell
python -m unittest discover -s tests -v
python demo.py
python benchmark.py --requests 200 --workers 8
# Optional, if Ruff is available:
ruff check .
ruff format --check .
```

Tests cover functional semantics, limits, malformed cursors, Unicode normalization,
tenant isolation, SQL parameterization, foreign keys, rollback, persistence and thread
races. They do not establish multi-host correctness, crash/power-loss durability,
authorization or production throughput. `schema/postgresql.sql` was not executed
against a PostgreSQL server during this review.
