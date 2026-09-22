# Organization chart: local LLD practice

Copied from `C:/Users/sange/PycharmProjects/test` into `LLD/org_chart`.
The original source directory is preserved. Source modules and existing tests are
retained; the original Git repository, virtual environment and IDE configuration
are not required here.

## Run locally

Python 3.11+; no cloud services or runtime dependencies:

```powershell
python src/main.py
```

Expected result: `Closest common group: Engineering`.

The original test suite uses pytest, a local development dependency:

```powershell
python -m pip install pytest
python -m pytest -q
```

Alternatively, `uv sync --group dev` followed by `uv run pytest -q` uses the
included project configuration and lock file.

## Design

- Immutable employee/group models: `src/models/datamodel.py`.
- Repository abstraction and in-memory implementation: `src/repository/`.
- Application service: `src/transformation/build_org_graph.py`.
- Typed domain errors and logging: `src/exceptions/` and `src/log/`.
- Demonstration: `src/main.py`; regression tests: `tests/`.

Supported operations: add groups/employees, move employees, move groups with cycle
rejection, and find the closest shared ancestor group for a collection of employees.
An employee belongs to one group; disconnected trees have no common group.

The query walks parent chains and intersects ancestor sets. For K employees and
maximum hierarchy height H, time and temporary space are O(KH); storage is O(G+E)
for groups and employees. No database or graph server is necessary for this exercise.

## Concurrency and production discussion

The service uses an RLock around reads and mutations. This protects callers sharing
ONE service instance. Sharing a repository between multiple service instances, or
mutating its public dictionaries directly, bypasses that protection. The migration
does not claim distributed safety or durable persistence.

Production-only extensions (not required to run locally): a transactional store,
tenant authorization, hierarchy versions and audit events. Cached ancestor paths
need invalidation after moves; binary lifting helps mostly-static trees but adds
update complexity. API replicas need database-level concurrency control, not just
one lock per Python process. Keep the interview implementation focused on invariants.

The original brainstorming notes are retained in `design.md`.
