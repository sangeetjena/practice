# Implementation review

## Implemented and checked

- `RateLimiter`: one instance-owned state dictionary, one atomic lock, injected
  monotonic clock, bounded key/customer count and explicit safe cleanup.
- `FixedWindow`: aligned periods and integer-valued costs; boundary doubling is
  part of the algorithm, not an exact rolling-window guarantee.
- `TokenBucket`: capped continuous refill and fractional cost using exact decimal
  `Fraction` arithmetic for supplied inputs. No background refill worker.
- `SlidingWindowLog`: accepted-event deque for `(now-W, now]`, distinct simultaneous
  events, unit costs, safe removal only after the newest event expires.
- `Policy[StateT]`: structural interface and strategy polymorphism. Algorithms own
  their state types; the engine only requires `last_seen_at` for cleanup.
- Frozen policy/decision dataclasses; private mutable state under the engine lock.
- `ValueError` for invalid input/clock and `CustomerCapacityExceeded` for exhausted
  state capacity. Neither is a successful quota-denial decision.

All handwritten functions/methods have docstrings. Public classes describe their
responsibilities. Tests explain boundary and concurrency expectations.

## Validation

`python -m unittest discover -v`: 22 passing tests, including a randomized trace
checked against an independent list-based oracle, real thread contention, and
cleanup safety. `python demo.py` demonstrates all three policies.

Ruff lint and formatting checks apply to the Python files. No throughput number
is claimed: this exercise has not been production-load-tested.

## Deliberately outside this implementation

No Redis, PostgreSQL, HTTP server, authentication, cross-process synchronization,
policy hot reload, request deduplication, distributed leases, queue shaper,
concurrency semaphore or adaptive controller is implemented. Sliding counter,
leaky-bucket policing and GCRA are HLD alternatives, not additional working policies.

State is lost on restart. Two processes have independent quotas. One lock serializes
all keys; cleanup scans under it. Maximum customer and log counts bound logical
cardinality, not memory bytes. Policy/clock callbacks must be trusted and fast.

## Production seams

Put identity validation, HTTP status mapping, metrics and sampled structured logging
in a thin adapter. Do not emit synchronous per-request logs while holding the lock.
Log infrastructure failures separately from ordinary denials; avoid raw keys/API
credentials and high-cardinality metric labels.

A Redis backend should expose **atomic check-and-consume**, not separate `get`
and `save` calls. Its script owns the whole transition. Redis time and Lua number
semantics differ from Python monotonic time and `Fraction`; define integer units,
safe numeric bounds, rounding and TTLs before implementing it.

For policy updates, keep immutable policy/state generations and an explicit migration
contract. Do not replace `_policy` or create a new full bucket for every version.
For multiple policies, define all-or-nothing debit and co-location rather than
sequentially consuming independent limiters and attempting unsafe refunds.

## Thirty-minute interview order

1. 0–4 min: clarify key, window/burst contract, cost, denial and deployment scope.
2. 4–8 min: define `Decision`, one state type and the four-method policy contract.
3. 8–18 min: implement one chosen policy and locked `try_acquire`.
4. 18–25 min: test boundary/refill, two customers, invalid input and contention.
5. 25–30 min: implement safe cleanup if required; explain restart and distributed
   extensions. Add the second/third policy as a follow-up, not a promise to type
   every algorithm plus all explanatory docstrings within thirty minutes.
