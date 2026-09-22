# Atlassian / Principal Engineer design practice

Five independent Python 3.11+ LLD implementations with runnable demos, meaningful
unit/concurrency tests, and detailed LLD/HLD design notes, all under `LLD`.
The previously created [tagging service](tagging-service/README.md) is also here.

## Start here

### Runnable implementation and test files

- **Organization Chart:** [design and local commands](org_chart/README.md),
  [implementation](org_chart/src/transformation/build_org_graph.py),
  [tests](org_chart/tests/test_organization_directory.py). Migrated independently;
  its tests use pytest and are not part of the standard-library runner below.

The README files describe the designs; the following Python files implement them:

- **Rate Limiter:** [implementation](rate-limiter/rate_limiter.py),
  [tests](rate-limiter/test_rate_limiter.py), [demo](rate-limiter/demo.py).
- **URL Router:** [implementation](url-router/router.py),
  [tests](url-router/test_router.py), [demo](url-router/demo.py).
- **Snake Game:** [implementation](snake-game/snake.py),
  [tests](snake-game/tests/test_snake.py), [demo](snake-game/demo.py).
- **File Collections:** [implementation](file-collections/file_collections/service.py),
  [tests](file-collections/tests/test_service.py), [demo](file-collections/demo.py).
- **Agent Ratings:** [implementation](agent-ratings/ratings.py),
  [tests](agent-ratings/tests/test_ratings.py), [demo](agent-ratings/demo.py).
- **Tagging Service:** [implementation](tagging-service/tagging_service/service.py),
  [transaction boundary](tagging-service/tagging_service/database.py),
  [tests](tagging-service/tests/test_service.py), [demo](tagging-service/demo.py).

The five new LLD implementations enforce concurrency within one process. The
tagging service uses SQLite transactions. Production multi-host scaling is described
in the HLD sections and is not implemented infrastructure.

### Design walkthroughs

1. [Rate Limiter](rate-limiter/README.md): atomic admission, fixed windows, token
   buckets, injected clocks, safe cleanup, distributed quotas.
2. [URL Router](url-router/README.md): segment trie, exact/parameter/wildcard
   precedence, backtracking, copy-on-write registration, routing control plane.
3. [Snake Game](snake-game/README.md): deque/set state machine, growth and collision
   invariants, optimistic command versions, authoritative game sessions.
4. [File Collections](file-collections/README.md): unique storage, multiple collection
   memberships, delta updates, consistent reporting, distributed aggregation.
5. [Agent Ratings](agent-ratings/README.md): exact averages, deterministic ranking,
   event deduplication, concurrent aggregation, durable leaderboard design.

Each implementation uses only the standard library. No downloads, service accounts,
database servers, or installation steps are required. The HLD sections describe
production extensions; these are not implemented HTTP/distributed services.

```powershell
# From this directory, using an installed Python 3.11+ interpreter:
python run_all.py --demos

# Include the SQLite-backed tagging implementation:
python run_all.py --include-tagging --demos

# Existing interpreter in this particular practice workspace:
& '../GCP/.cache/python/cpython-3.11.13-windows-x86_64-none/python.exe' run_all.py --demos

# Optional lint/format verification, if Ruff is installed:
ruff check .
ruff format --check .
```

The runner launches each project in a separate process, fails on unsuccessful
tests/demos, and imposes a timeout. For individual commands see each README. Modules
use descriptive names and immutable public results. Internal locks are explicit:
the designs do not rely on the Python GIL for compound-operation correctness.

## How to use these in an interview

These are preparation examples, not an employer's answer key or guarantee of a
particular question. Start with the problem contract and implement the smallest
complete version; add the extensions the interviewer requests.

### Clarify

Ask questions that change behavior: identity, validation, ordering, failure semantics,
concurrency, storage lifetime, scale, and consistency. State assumptions and move
forward rather than waiting for the interviewer to design the solution.

### Compare and choose

Explain two plausible approaches and their costs. Name the data structure and link
it to the operations you need. Do not add interfaces solely to recite a pattern.

### Implement

State invariants before tricky code. Use clear names, validate before mutation,
keep side effects outside locks where possible, return immutable values, and run
the simplest case early. Distinguish invalid input from a legitimate negative result.

### Test

Cover happy paths, empty state, exact boundaries, invalid inputs, idempotency,
multi-operation state transitions, concurrency races, and regression after extension.
Use fake time and barriers rather than sleep-dependent assertions. A passing example
is weaker evidence than a test that targets the failure mode.

### Evolve

Explain exactly which contract and invariant the new requirement changes. Preserve
existing behavior with regression tests. For concurrency, identify the entire
critical section and the linearization point. For storage, distinguish one-process
atomicity from cross-process transactions and distributed consistency.

### Discuss HLD when requested

Establish workload, capacity, latency/availability objectives, API boundaries,
persistence, routing/partitioning, replication, authorization, failure handling,
observability, recovery, and cost. No numeric production SLO here is a measured claim.

## A 60-minute rehearsal

- 0–7: clarify, compare approaches, commit to one.
- 7–12: API, state, invariants, complexity.
- 12–35: implement and execute focused tests.
- 35–48: add a follow-up while keeping previous tests passing.
- 48–57: boundaries, concurrency, failure behavior.
- 57–60: summarize trade-offs and honest limitations.

Suggested follow-ups: limiter credits and safe eviction; router literal dead-end;
snake moving-tail collision; file resize plus membership changes; ratings duplicate
events and tie-breaking. A useful unblock sequence is: reduce to a small failing
example, inspect state, revisit the invariant, fix, and run the regression test.

## Scope and evidence

Validation after review on 21 September 2026: 57 tests across five suites plus 30
tagging tests (87 total), and all six demos passed. Tests cover concurrent admission,
registration, command processing,
aggregation, deduplication and snapshot consistency. Ruff lint and formatting are
checked using the configuration in this directory. These correctness checks are
not production throughput benchmarks or distributed failure tests.

All five services are process-local, in-memory reference implementations. They
intentionally do not claim restart durability, distributed quotas, network APIs,
authentication, consensus, or production load capacity. Their READMEs explain how
to add those capabilities without silently changing the current semantics.

## Code review: best practices and remaining limits

Reviewed state invariants, synchronization, encapsulation, validation, complexity,
and failure-path tests. This is an engineering assessment, not an employer certification.

### Corrections

- Rate limiter: float subtraction could lose tiny costs against large buckets and
  permit excess admission. Exact internal fraction arithmetic now preserves costs.
  Decimal fixed-window boundaries and oversized clock inputs have regression tests.
- Tagging: deeply nested cursor JSON is rejected as invalid input; surrogate keys
  are rejected before database encoding; boolean cursor versions are rejected.
- Router, ratings, collections: ASCII DEL is rejected consistently with their rules.
- Runner: `--include-tagging` includes the sixth service in integrated verification.

### Modularity assessment

- Rate limiter uses a genuine Strategy interface and injected clock. Engine owns
  synchronization and key lifecycle; policies own quota semantics.
- Router separates parsing, immutable trie construction, publication and traversal.
  User handlers execute outside the registry; total route count remains uncapped.
- Snake separates immutable values and game logic from rendering/networking. Separate
  State-pattern classes would not improve this simple running/game-over contract.
  Introduce growth/food policies when the corresponding requirement is added.
- Ratings separates deduplication, immutable aggregates and snapshot ranking. Sorting
  outside the lock reduces contention. Additional ranking interfaces are unnecessary
  until multiple ranking rules are required.
- Collections protects coherent delta updates and sorts detached snapshots outside
  the lock. Global versions are safe but conflict across unrelated file updates.
- Tagging separates models, transactions and cursors, but application logic and SQL
  remain coupled in `service.py`. A second backend would justify an atomic use-case
  store interface; generic CRUD wrappers must not fragment transactions.

### Limits of verification

The in-memory examples serialize mutations under a service/game lock. They do not
guarantee lock fairness, latency deadlines, crash durability, multi-process correctness
or multi-region consistency. SQLite tagging has one writer per file. No distributed
deployment or production load test was performed. Type hints and Ruff improve
maintainability; a full static type-checking gate has not been added. Custom policy
and clock callbacks are trusted dependencies. HLD notes describe production work.
