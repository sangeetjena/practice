# Transactional storage and execution ownership

Source: `observe_agent/cloud/database.py`.

## How the code works

Database.submit commits cloud_incidents and cloud_events in one transaction. Database.append uses revision/status comparison to admit a single new input, stores its author, and enqueues processing. Database.incident_lock uses a dedicated PostgreSQL advisory-lock connection for graph execution.

## Example

An Acme POST for inc-1 creates session S1/run R1/event E1. A same-key replay returns S1 instead of adding E2. A new message after completion advances to R2 and invalidates the previous proposal digest.

## Debugging and limits

Database.get('acme', 'inc-1') filters both columns. A Globex lookup does not see that row. Two workers cannot hold the same incident lock. SQLite lock fallback is only for single-process tests.

See [the complete sequence](../CLOUD_RUNTIME.md) and [module map](../MODULE_GUIDE.md).

