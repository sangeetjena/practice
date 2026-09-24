# Revised interview scope

The primary implementation is now a small **in-memory** service intended for a
30-minute coding exercise including tests. `README.md` is the current practice guide.

## Removed from the timed implementation

- SQLite `Database`, connection/transaction setup, WAL and persistence fixtures.
- Generic `Page`, cursor encoding/validation and query-scoped keyset pagination.
- `ResourceTags` version snapshots, `VersionConflict`, bulk replacement and expected versions.
- Prefix/ALL/ANY search, filter/cursor combinations and the benchmark harness.
- Long method templates and the multi-module error/model framework.

## Retained

- `TaggingService`: one class with all small operations and a single per-instance lock.
- Immutable `ResourceKey` and `Tag`; built-in `ValueError`, small `NotFound` and `Conflict` types.
- Normalized get-or-create, stable IDs, rename, delete-unused and metadata lookup.
- Idempotent attach/detach; direct resource-to-tags and tag-to-resources indexes.
- Immutable query results and focused behavior/concurrency tests.

## Deliberate API changes

```python
# Before: Database initialization + TaggingService(database, tenant_id)
service = TaggingService("acme")

# Before: paginated Page and ResourceTags(version, tag_ids)
service.get_resource_tags(resource)  # frozenset[str]
service.list_resources(tag_id)       # frozenset[ResourceKey]

# Before: expected_version required
service.rename_tag(tag_id, "New name")
service.delete_tag(tag_id)
```

Attach/detach return None. Name conflicts and used-tag deletion still fail before
mutation. Unknown tag IDs raise NotFound; malformed names/resource identities raise
ValueError. There is no root custom exception hierarchy and no version-based stale
write detection. Services for the same tenant must be reused by the caller; this
module is not a registry or a process-shared database.

The [previous persistent version](https://github.com/sangeetjena/practice/tree/6cfe841788c3a27028194ed98b31ea7a4aff2c5f/LLD/tagging-service)
remains available for studying those follow-ups. Existing production HLD/SQL material
and earlier Google Docs discussions describe a larger design; they must not be read
as claims about the current timed implementation.
