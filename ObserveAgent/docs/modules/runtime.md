# Tenant graph construction and durable event processing

Source: `observe_agent/cloud/runtime.py`.

## How the code works

GraphFactory creates remote Chroma, tenant-specific tool policies and a PostgreSQL checkpointer. Worker.process locks an incident, starts/resumes its event, then atomically records the result and event completion.

## Example

E1 creates report R1 and pauses. A fresh worker receives approval E2 and loads R1's persisted interrupt. Message E3 creates a new run with recent messages and the previous summary.

## Debugging and limits

Exceptions persist only their class in event state. The first four attempts can retry; the fifth becomes dead. Model context is bounded; older messages remain in SQL.

See [the complete sequence](../CLOUD_RUNTIME.md) and [module map](../MODULE_GUIDE.md).

