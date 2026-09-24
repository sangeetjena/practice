# Tagging service: 30-minute coding round

**Practice this version first.** One service class owns the state. Two frozen
dataclasses represent resources and tags; two small exceptions describe missing
tags and conflicts. No database setup, repository interfaces, cursor framework,
HTTP framework or background jobs are needed.

The older persistent implementation was too large for the time limit. It remains
[available in Git history](https://github.com/sangeetjena/practice/tree/6cfe841788c3a27028194ed98b31ea7a4aff2c5f/LLD/tagging-service).
This is an intentional API/scope change, not a compatible persistence refactor.

## 1. Clarify the contract (minutes 0-3)

- One long-lived service instance per tenant; multiple product types can share tags.
- Resource identity is `(product, resource_type, resource_id)`; external IDs can collide.
- Tag names are NFKC-normalized, trimmed and case-insensitive for uniqueness.
- Creating an existing name returns the existing tag; UUID identity survives renaming.
- Attach/detach are idempotent. An unknown tag ID raises `NotFound`.
- Delete only unused tags; deleting a used tag or renaming to another tag's name raises `Conflict`.
- No database persistence, pagination, permissions or advanced search in this iteration.

## 2. Explain the data structures (minutes 3-5)

```text
tags:          tag_id -> immutable Tag
names:         normalized_name -> tag_id
resource_tags: ResourceKey -> set[tag_id]
tag_resources: tag_id -> set[ResourceKey]
```

**Invariant:** a `(resource, tag_id)` association appears in both indexes or neither.
One lock protects all reads and writes within the tenant service. Return frozen
dataclasses and `frozenset` copies so callers cannot corrupt the indexes.

Why two indexes? Both access patterns avoid scanning every assignment. The trade-off
is O(T + A) memory with two copies of each association, for T tags and A assignments.
Create/get/rename/delete/attach/detach use expected O(1) dictionary/set operations,
excluding name processing. Returning results costs O(k) for k matching entries.
Output is unordered and unpaginated; it is intended for small interview datasets.

## 3. Implement the core (minutes 5-20)

Write [service.py](tagging_service/service.py) in this order:

1. `ResourceKey`, `Tag`, `NotFound`, `Conflict`, and the name-validation helper.
2. Constructor: four dictionaries and a `Lock`.
3. `create_tag` and `get_tag`: normalized uniqueness and stable IDs.
4. `attach_tag`, `detach_tag`: change both assignment indexes inside one lock.
5. `get_resource_tags`, `list_resources`: return immutable copies.
6. `rename_tag`, `delete_tag`: validate before changing the catalog.

You can write everything in one file during the interview. The package export file
and demo are repository conveniences, not extra architecture to reproduce.
Short docstrings explain the reference code; do not type long documentation during
the timed attempt. Rehearse the full solution with a timer rather than assuming a
line count guarantees a particular completion time.

## 4. Write and run tests (minutes 20-28)

[Six tests](tests/test_service.py) cover:

1. Duplicate normalized names and invalid input.
2. Idempotent attach/detach, both indexes, cross-product IDs and detached snapshots.
3. Rename preserves identity/assignments and conflicts leave state unchanged.
4. Used-tag deletion, missing IDs and name reuse after deletion.
5. Separate tenant instances do not share data.
6. Concurrent creation produces one tag and concurrent attachments are all retained.

Prioritize the first four while coding; the last two are short concurrency/isolation
checks to rehearse too. The checked-in suite contains all six. There are no sleeps,
database fixtures, generated load or external services.

From `LLD/tagging-service`, in Windows/PyCharm PowerShell:

```powershell
uv run --no-project --python 3.11 python demo.py
uv run --no-project --python 3.11 python -m unittest discover -s tests -v
```

Or use an installed Python with `python demo.py` and
`python -m unittest discover -s tests -v`. Tests use only the standard library.
The repository's `LLD/run_all.py --include-tagging` continues to discover this suite.

## 5. Explain limits and extensions (minutes 28-30)

- **Concurrent readers/writers:** the same lock protects both indexes. A reader sees
  state before or after an operation, never a partial update. Each API call is atomic;
  a sequence of separate calls is not a transaction.
- **Conflicting edits:** concurrent renames serialize; the last successful rename wins.
  To reject stale user edits, add an expected version later. A lock alone does not do that.
- **Object lifetime:** create the service at application startup and reuse it. A tenant
  registry must return the same instance for subsequent requests. Two constructors with
  the same tenant ID create separate stores; tenant IDs are labels, not global storage keys.
- **Persistence/scale:** restart loses everything. A lock does not coordinate processes.
  Replace the memory storage with database transactions, unique constraints and indexes
  when durability/multiple replicas become requirements. Bound request/result sizes then.
- **Security:** the caller must supply validated `ResourceKey` objects and trusted tenant
  identities. Type annotations are not JSON validation or authentication. Product ACLs
  belong in an adapter; this engine does not check whether a product resource exists.
- **Additional search:** multi-tag ALL/ANY becomes intersection/union of reverse sets;
  prefix search, pagination and hot-tag scaling are follow-ups, not prerequisites.
- **Patterns:** composition and value objects are sufficient. Introduce a storage Protocol
  when a second implementation is actually required; no forced inheritance hierarchy.
- **Logging:** log request outcomes at the caller boundary, outside the lock. A logging
  framework is not required to demonstrate the domain behavior in this coding round.

The [PostgreSQL schema](schema/postgresql.sql) remains an optional HLD reference and
is not executed by this service. See [scope changes](docs/IMPLEMENTATION_REVIEW.md).
