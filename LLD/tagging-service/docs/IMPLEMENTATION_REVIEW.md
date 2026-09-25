# Current interview scope

The runnable implementation is an in-memory tenant service; README.md is the current
practice guide. Earlier Google Docs/HLD persistence discussions describe extensions.

## Read consistency

Writers hold the per-instance lock. They replace affected membership frozensets and
publish copied metadata/index dictionaries as one tuple. Reads capture published
values without acquiring that lock; published containers are never mutated.
Top-K captures the complete tuple before iterating, so concurrent deletion/rename
cannot produce a missing metadata lookup inside the selected view.

Publication is synchronous before a write returns. An overlapping read may use the
previous view; this is not a background replication system. The intended runtime is
normal GIL-enabled CPython. Copying maps and affected sets makes writes more expensive
and increases transient memory; this trade-off is explicit in the practice guide.

## Top-K contract

`top_k_tags(k) -> tuple[tuple[Tag, int], ...]` ranks this tenant's used tags by distinct
attached resources, descending, then tag ID descending. Attach retries do not add
votes; detach reduces the count; unused/deleted tags are excluded. Zero k returns
empty; negative/noninteger/bool k raises ValueError. This is popularity, not a rolling
time-window score. Heap selection is computed on demand from the published view.

## Test scope

Four tests cover the catalog, assignments/snapshots, ranking/tenant isolation and
read completion while a separate thread holds the writer lock. This is a focused
interview suite, not a production concurrency stress or portability certification.

## Still excluded

SQLite/PostgreSQL adapters, cursor pagination, prefix/Boolean search, bulk replacement,
expected versions, benchmarks, authentication and multi-process coordination. The
[previous persistent version](https://github.com/sangeetjena/practice/tree/6cfe841788c3a27028194ed98b31ea7a4aff2c5f/LLD/tagging-service)
is retained in Git history. No new interface or class hierarchy was added for ranking.
