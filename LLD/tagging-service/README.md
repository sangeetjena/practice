# Tagging service: 30-minute coding round

One in-memory service per tenant, two frozen dataclasses, two small exceptions.
No database setup, repository hierarchy, background jobs or HTTP framework.

## Contract to clarify (0-3 minutes)

- Resources use `(product, resource_type, resource_id)`; IDs can collide across products.
- Names use NFKC + trim + casefold uniqueness. Repeated creation returns the existing tag.
- Rename preserves tag ID; delete only unused tags. Conflicts raise `Conflict`.
- Attach/detach are idempotent. Unknown tag IDs raise `NotFound`.
- Reads acquire **no application lock** and may observe the previous published snapshot.
- `top_k_tags(k)` returns `(Tag, resource_count)` pairs, highest count first. Equal
  counts use tag ID descending for a deterministic tie-break. Unused tags are excluded.
- `k=0` returns empty; k larger than the used-tag count returns all used tags.
  Negative, non-integer and boolean k values raise `ValueError`.
- Ranking is **current distinct-resource popularity**, not a time-windowed trend score.

## Data model and read behavior (3-5 minutes)

```text
tags:          tag_id -> frozen Tag
names:         normalized_name -> tag_id        (writers only)
resource_tags: ResourceKey -> frozenset[tag_id]
tag_resources: tag_id -> frozenset[ResourceKey]
published:     (tags.copy(), resource_tags.copy(), tag_resources.copy())
```

Writers hold one lock, replace the affected frozensets, then publish all three copied
dictionaries with one `_view` assignment. Published dictionaries are private and
never modified. Their values are immutable, so readers can safely use an older view.
`top_k_tags` captures `_view` once before iteration; it cannot mix names from one
version with counts from another. Reads need no locking or copying of result sets.

**Eventual consistency permits stale results, not unsafe collection iteration.**
This small CPython implementation publishes synchronously before a successful write
returns; overlapping reads may see the previous view. It does not implement distributed
replication or asynchronous refresh. Separate read calls need not share one snapshot.
The application-lock-free design targets normal GIL-enabled CPython; it is not a
portable claim of wait-free execution across Python runtimes.

## Coding order (5-20 minutes)

1. Write `ResourceKey`, `Tag`, `NotFound`, `Conflict` and name validation.
2. Initialize four dictionaries, the writer lock and the published view.
3. Create/get, rename/delete; publish after each catalog mutation.
4. Attach/detach using set union/difference; publish after updating both directions.
5. Read methods use only `_view`, never `_lock`.
6. `top_k_tags`: capture the view, compute set lengths, use `heapq.nlargest`.

```python
service = TaggingService("acme")  # Reuse this instance for this tenant's requests.
tag = service.create_tag("Backend")
service.attach_tag(ResourceKey("jira", "issue", "123"), tag.tag_id)
service.top_k_tags(3)             # ((Tag(..., "Backend"), 1),)
```

Implementation: [service.py](tagging_service/service.py). You can put it all in one
file during an interview; package exports and the demo are repository conveniences.
Keep docstrings brief and rehearse with a timer rather than assuming a line count
guarantees completion time.

## Essential tests (20-28 minutes)

[Four short tests](tests/test_service.py):

1. Catalog: normalized duplicate, invalid name, rename conflict and deletion.
2. Assignments: retry safety, both indexes, used-tag deletion and old snapshot stability.
3. Top-K: counts, detach updates, ties, k boundaries and tenant isolation.
4. Lock-free reads: another thread finishes all read APIs while the writer lock is held.

No database fixtures, load benchmarks or sleep-based synchronization. Run from
`LLD/tagging-service` in Windows/PyCharm PowerShell:

```powershell
uv run --no-project --python 3.11 python demo.py
uv run --no-project --python 3.11 python -m unittest discover -s tests -v
```

An installed Python can run the same commands without the `uv run` prefix.
`LLD/run_all.py --include-tagging` still discovers the suite.

## Trade-offs to explain (28-30 minutes)

- **Read speed:** metadata and membership lookups are expected O(1); results are immutable.
  Top-K examines T tags and uses O(T log min(k,T)) work for k >= 2, O(T) for k=1,
  and O(min(k,T)) candidate memory. It does not sort all tags when k is small.
- **Write cost:** snapshot publication copies dictionary entries, O(T + R), where R is
  the number of currently tagged resources. Attach/detach also copy affected frozensets,
  proportional to their sizes. This moves work from readers to writers; it is a small
  read-oriented interview example, not a production hot-tag storage design.
- **Memory:** current state is O(T + R + A), for A assignments. Old views remain alive
  while readers reference them. Copy-on-write raises peak memory during updates.
- **Concurrency:** writers serialize, preserving name uniqueness and both indexes.
  Renames are last-successful-writer-wins; there is no stale-version check.
- **Tenancy/lifetime:** each tenant needs one reused instance. Two constructors for the
  same tenant create separate stores. Authentication and resource ACLs belong outside.
- **Production follow-up:** replace full snapshot copying with a database/read projection
  or persistent data structures. Add incremental ranking and event-time windows only if
  required. The local code has no persistence, distributed state or pagination.

[Older persistent implementation](https://github.com/sangeetjena/practice/tree/6cfe841788c3a27028194ed98b31ea7a4aff2c5f/LLD/tagging-service).
The [PostgreSQL schema](schema/postgresql.sql) is an optional HLD reference, not executed.
